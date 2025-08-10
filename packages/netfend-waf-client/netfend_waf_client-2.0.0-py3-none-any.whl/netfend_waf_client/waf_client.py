"""
WAF Client SDK - Enhanced Version with Fully Dynamic Configuration System
Python implementation that fetches ANY protections dynamically from /v1/user/me endpoint
NO HARDCODED protection names - completely flexible
"""

import asyncio
import hashlib
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import re

import aiohttp
import requests
from flask import Flask, request, jsonify, Response
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


class WAFClient:
    def __init__(self, options: Dict[str, Any] = None):
        if not options:
            options = {}
            
        if not options.get('apiKey'):
            raise ValueError('WAF API Key is required')
            
        self.api_key = options['apiKey']
        self.config_endpoint = options.get('configEndpoint', 'https://graphnet.emailsbit.com/waf/v1/user/me')
        self.waf_endpoint = options.get('wafEndpoint', 'https://graphnet.emailsbit.com/waf/v1/validate')
        
        # Cache configuration
        self.config_cache = None
        self.last_config_fetch = 0
        self.config_refresh_interval = options.get('configRefreshInterval', 10000) / 1000  # 10 seconds
        self.config_timeout = options.get('configTimeout', 5000) / 1000  # 5 seconds
        
        # Keep track of discovered protections for logging purposes only
        self.discovered_protections = set()
        
        # Fallback configuration (used if API is unavailable) - NO HARDCODED PROTECTIONS
        self.fallback_config = {
            'enabled': options.get('enabled', True),
            'blockOnError': options.get('blockOnError', True),
            'logRequests': options.get('logRequests', False),
            'responseType': options.get('responseType', 'rest'),
            'onWafError': options.get('onWafError', 'allow'),
            'timeout': options.get('timeout', 5000) / 1000,
            'cacheTimeout': options.get('cacheTimeout', 60000) / 1000,
            'protections': {},  # Empty - will be populated dynamically from API
            'validatedMethods': ['POST', 'PUT', 'PATCH', 'DELETE'],
            'ignoredPaths': ['/health'],
            'enableCache': True,
            'customHeaders': {}
        }
        
        self.cache = {}
        self.rate_limit_map = defaultdict(list)
        self.config_update_timer = None
        
        # Setup logging
        self.logger = logging.getLogger('WAFClient')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s [%(name)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)  # Default to WARNING, will be updated based on config
        
        # Initialize configuration
        self._initialize_config()
        
    def _initialize_config(self):
        """Initialize configuration by fetching from API or using fallback"""
        try:
            self._fetch_configuration()
            self._start_config_update_loop()
        except Exception as error:
            print(f"⚠️  [WAF Client] Failed to fetch initial configuration, using fallback: {str(error)}")
            self.config_cache = self.fallback_config
            self._update_logger_level()
            
    def _fetch_configuration(self):
        """Fetch configuration from the API endpoint"""
        try:
            headers = {
                'Authorization': self.api_key,
                'Content-Type': 'application/json',
                'X-WAF-Client': 'python'
            }
            
            response = requests.get(
                self.config_endpoint,
                headers=headers,
                timeout=self.config_timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Config API returned {response.status_code}: {response.text}")
                
            response_data = response.json()
            
            if not response_data.get('success'):
                raise Exception(f"Config API returned error: {response_data.get('message', 'Unknown error')}")
                
            waf_setting = response_data['wafSetting']
            
            # Transform API response to internal config format - FULLY DYNAMIC
            new_config = {
                'enabled': waf_setting['enabled'],
                'blockOnError': waf_setting['blockOnError'],
                'logRequests': waf_setting['logRequests'],
                'responseType': waf_setting['responseType'],
                'onWafError': waf_setting['onWafError'],
                'timeout': waf_setting['timeout'] / 1000,  # Convert to seconds
                'cacheTimeout': waf_setting['cacheTimeout'] / 1000,
                
                # DYNAMIC protections - accept ANY protection from API
                'protections': self._transform_protections_dynamically(waf_setting.get('protections', {})),
                
                # Transform validatedMethods from object to array
                'validatedMethods': [
                    method.upper() for method, enabled in waf_setting.get('validatedMethods', {}).items()
                    if enabled
                ],
                
                'ignoredPaths': waf_setting.get('ignoredPaths', []),
                
                # Add metadata
                'configFetchedAt': datetime.now().isoformat(),
                'configUpdatedAt': waf_setting.get('updatedAt'),
                
                'enableCache': True,
                'customHeaders': {}
            }
            
            # Check if configuration actually changed
            config_changed = (not self.config_cache or 
                            json.dumps(self.config_cache, sort_keys=True) != json.dumps(new_config, sort_keys=True))
            
            if config_changed:
                old_config = self.config_cache
                self.config_cache = new_config
                self.last_config_fetch = time.time()
                self._update_logger_level()
                
                if self.config_cache['logRequests']:
                    enabled_protections = [
                        name for name, config in new_config['protections'].items()
                        if config['enabled']
                    ]
                    
                    changes = self._get_config_changes(old_config, new_config) if old_config else ['initial_load']
                    
                    self.logger.info(f"🔄 [WAF Client] Configuration updated: "
                                   f"enabled={new_config['enabled']}, "
                                   f"protections={enabled_protections}, "
                                   f"validatedMethods={new_config['validatedMethods']}, "
                                   f"ignoredPaths={len(new_config['ignoredPaths'])}, "
                                   f"responseType={new_config['responseType']}, "
                                   f"updatedAt={new_config['configUpdatedAt']}, "
                                   f"changed={changes}")
                
                # Clear cache when configuration changes
                if old_config and self.cache:
                    self.cache.clear()
                    if self.config_cache['logRequests']:
                        self.logger.info('🗑️  [WAF Client] Request cache cleared due to config change')
                        
            return new_config
            
        except Exception as error:
            print(f"❌ [WAF Client] Failed to fetch configuration: {str(error)}")
            print(f"    Endpoint: {self.config_endpoint}")
            print(f"    Is network error: {not hasattr(error, 'response')}")
            
            # If we have a cached config, keep using it
            if self.config_cache:
                if self.config_cache['logRequests']:
                    self.logger.info('📋 [WAF Client] Using cached configuration due to fetch error')
                return self.config_cache
                
            # Otherwise, use fallback
            self.config_cache = self.fallback_config
            self._update_logger_level()
            return self.fallback_config
    
    def _transform_protections_dynamically(self, api_protections: Dict) -> Dict:
        """
        Transform API response protections to internal format - FULLY DYNAMIC
        Accepts ANY protection type returned by the API, no hardcoded names
        """
        transformed_protections = {}
        
        if not api_protections or not isinstance(api_protections, dict):
            print('⚠️  [WAF Client] No protections received from API, using empty config')
            return {}
        
        # Process ALL protections from API response dynamically
        for protection_name, config in api_protections.items():
            # Validate and normalize the protection configuration
            normalized_config = self._normalize_protection_config(config, protection_name)
            transformed_protections[protection_name] = normalized_config
            
            # Track new protections for informational purposes
            if protection_name not in self.discovered_protections:
                self.discovered_protections.add(protection_name)
                
                print(f"🆕 [WAF Client] New protection discovered: {protection_name}")
                print(f"    enabled: {normalized_config['enabled']}")
                print(f"    config: {normalized_config}")
        
        return transformed_protections
    
    def _normalize_protection_config(self, config: Any, protection_name: str) -> Dict:
        """
        Normalize protection configuration to ensure consistent structure
        Handles various possible config formats from the API
        """
        # Handle boolean format
        if isinstance(config, bool):
            return {'enabled': config}
        
        # Handle object format
        if isinstance(config, dict):
            normalized = {
                'enabled': config.get('enabled', True),  # Default to True if not specified
                **{k: v for k, v in config.items() if k != 'enabled'}  # Preserve any additional properties
            }
            
            # Ensure enabled is always a boolean
            if not isinstance(normalized['enabled'], bool):
                print(f"⚠️  [WAF Client] Invalid enabled value for {protection_name}: {normalized['enabled']}, defaulting to true")
                normalized['enabled'] = True
            
            return normalized
        
        # Handle unexpected formats
        print(f"⚠️  [WAF Client] Unexpected config format for {protection_name}: {config}, defaulting to enabled: true")
        return {'enabled': True}
            
    def _get_config_changes(self, old_config: Dict, new_config: Dict) -> List[str]:
        """Compare configurations and return list of changes"""
        changes = []
        
        if old_config['enabled'] != new_config['enabled']:
            changes.append(f"enabled: {old_config['enabled']} → {new_config['enabled']}")
            
        if old_config['responseType'] != new_config['responseType']:
            changes.append(f"responseType: {old_config['responseType']} → {new_config['responseType']}")
            
        # Check protection changes - DYNAMIC comparison
        all_protections = set(old_config['protections'].keys()) | set(new_config['protections'].keys())
        
        for protection in all_protections:
            old_enabled = old_config['protections'].get(protection, {}).get('enabled', False)
            new_enabled = new_config['protections'].get(protection, {}).get('enabled', False)
            
            if old_enabled != new_enabled:
                changes.append(f"{protection}: {old_enabled} → {new_enabled}")
                
        # Check method changes
        old_methods = ','.join(sorted(old_config['validatedMethods']))
        new_methods = ','.join(sorted(new_config['validatedMethods']))
        if old_methods != new_methods:
            changes.append(f"validatedMethods: [{old_methods}] → [{new_methods}]")
            
        return changes if changes else ['no_changes']
        
    def _start_config_update_loop(self):
        """Start the configuration update loop"""
        if self.config_update_timer:
            self.config_update_timer.cancel()
            
        def update_config():
            try:
                self._fetch_configuration()
            except Exception:
                pass  # Error already logged in _fetch_configuration
            finally:
                # Schedule next update
                self.config_update_timer = threading.Timer(self.config_refresh_interval, update_config)
                self.config_update_timer.daemon = True
                self.config_update_timer.start()
                
        self.config_update_timer = threading.Timer(self.config_refresh_interval, update_config)
        self.config_update_timer.daemon = True
        self.config_update_timer.start()
        
        if self.config_cache and self.config_cache['logRequests']:
            self.logger.info(f'🔄 [WAF Client] Started config refresh loop ({self.config_refresh_interval}s interval)')
            
    def _stop_config_update_loop(self):
        """Stop the configuration update loop"""
        if self.config_update_timer:
            self.config_update_timer.cancel()
            self.config_update_timer = None
            
            if self.config_cache and self.config_cache['logRequests']:
                self.logger.info('⏹️  [WAF Client] Stopped config refresh loop')
                
    def _update_logger_level(self):
        """Update logger level based on current configuration"""
        if self.config_cache and self.config_cache['logRequests']:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
            
    def get_current_config(self) -> Dict:
        """Get current configuration"""
        return self.config_cache or self.fallback_config
        
    def validate_protection_settings(self):
        """
        Validate protection settings - DYNAMIC validation
        No hardcoded protection names, validates structure only
        """
        config = self.get_current_config()
        
        for key, value in config['protections'].items():
            if not isinstance(value.get('enabled'), bool):
                self.logger.warning(f"⚠️  [WAF Client] Protection {key}.enabled must be boolean, got {type(value.get('enabled'))}")
                config['protections'][key]['enabled'] = True
        
        # Log discovered protections for debugging
        if config['logRequests'] and self.discovered_protections:
            self.logger.info(f"🔍 [WAF Client] Discovered protections: {sorted(list(self.discovered_protections))}")
                
    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored"""
        config = self.get_current_config()
        return any(ignored_path.lower() in path.lower() for ignored_path in config['ignoredPaths'])
        
    def should_validate_method(self, method: str) -> bool:
        """Check if method should be validated"""
        config = self.get_current_config()
        return method.upper() in config['validatedMethods']
        
        
    def create_request_hash(self, method: str, path: str, body: Any, headers: Dict[str, str]) -> Optional[str]:
        """Create hash for request caching"""
        config = self.get_current_config()
        if not config['enableCache']:
            return None
            
        data = {
            'method': method,
            'path': path,
            'body': body,
            'headers': {
                'user-agent': headers.get('user-agent', ''),
                'content-type': headers.get('content-type', '')
            },
            'protections': config['protections'],
            'configHash': hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
        }
        
        hash_string = json.dumps(data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
        
    def check_cache(self, hash_key: str) -> Optional[Dict]:
        """Check if result is cached"""
        config = self.get_current_config()
        if not hash_key or not config['enableCache'] or hash_key not in self.cache:
            return None
            
        cached = self.cache[hash_key]
        if time.time() - cached['timestamp'] > config['cacheTimeout']:
            del self.cache[hash_key]
            return None
            
        return cached['result']
        
    def save_to_cache(self, hash_key: str, result: Dict):
        """Save result to cache"""
        config = self.get_current_config()
        if not hash_key or not config['enableCache']:
            return
            
        self.cache[hash_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
    def start_cache_cleaner(self):
        """Start cache cleaner timer"""
        config = self.get_current_config()
        if not config['enableCache']:
            return
            
        def clean_cache():
            now = time.time()
            
            # Clean cache
            expired_keys = [
                key for key, data in self.cache.items()
                if now - data['timestamp'] > config['cacheTimeout']
            ]
            for key in expired_keys:
                del self.cache[key]
                
                    
            # Schedule next cleanup
            timer = threading.Timer(config['cacheTimeout'], clean_cache)
            timer.daemon = True
            timer.start()
            
        timer = threading.Timer(config['cacheTimeout'], clean_cache)
        timer.daemon = True
        timer.start()
        
    async def validate_request_async(self, method: str, path: str, headers: Dict[str, str], 
                                   body: Any = None, query: Dict = None, params: Dict = None,
                                   client_ip: str = 'unknown') -> Dict:
        """Async version of request validation"""
        config = self.get_current_config()
        
        try:
                
            payload = {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body,
                'query': query or {},
                'params': params or {},
                'timestamp': datetime.now().isoformat(),
                'clientIp': client_ip,
                'userAgent': headers.get('user-agent', ''),
                
                # Send current protection settings to server - DYNAMIC
                'protections': config['protections'],
                
                'clientInfo': {
                    'apiKey': self.api_key,
                    'version': '2.1.0',
                    'responseType': config['responseType'],
                    'configFetchedAt': config.get('configFetchedAt'),
                    'configUpdatedAt': config.get('configUpdatedAt')
                }
            }
            
            if config['logRequests']:
                enabled_protections = [
                    name for name, prot_config in config['protections'].items()
                    if prot_config['enabled']
                ]
                config_age = None
                if config.get('configFetchedAt'):
                    config_age = str(int((time.time() - datetime.fromisoformat(config['configFetchedAt']).timestamp()))) + 's'
                
                self.logger.info(f"🔍 [WAF Client] Sending for validation: "
                               f"method={method}, path={path}, hasBody={bool(body)}, "
                               f"protections={enabled_protections}, ip={client_ip}, "
                               f"configAge={config_age or 'unknown'}")
                
            request_headers = {
                'Content-Type': 'application/json',
                'Authorization': self.api_key,
                'X-WAF-Client': 'python',
                'X-WAF-Response-Type': config['responseType'],
                **config['customHeaders']
            }
            
            timeout = aiohttp.ClientTimeout(total=config['timeout'])
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.waf_endpoint,
                    json=payload,
                    headers=request_headers
                ) as response:
                    response_data = await response.json()
                    
                    if config['logRequests']:
                        applied_protections = []
                        if 'appliedProtections' in response_data:
                            applied_protections = [
                                name for name, prot_config in response_data['appliedProtections'].items()
                                if prot_config.get('enabled', False)
                            ]
                            
                        self.logger.info(f"📨 [WAF Client] Server response: "
                                       f"status={response.status}, "
                                       f"blocked={response_data.get('blocked', False)}, "
                                       f"reason={response_data.get('reason')}, "
                                       f"violations={response_data.get('validationResults', {}).get('totalViolations', 0)}, "
                                       f"appliedProtections={applied_protections}")
                    
                    return response_data
                    
        except asyncio.TimeoutError:
            if config['logRequests']:
                self.logger.error("❌ [WAF Client] Network/timeout error: Timeout")
                
            if config['onWafError'] == 'block' or config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Unable to connect to security service',
                    'error': {'type': 'TIMEOUT', 'timeout': True}
                }
            
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_NETWORK_ERROR',
                'message': 'Security validation unavailable, request allowed',
                'warning': True
            }
            
        except Exception as error:
            if config['logRequests']:
                error_type = 'NETWORK_ERROR' if not hasattr(error, 'status') else 'HTTP_ERROR'
                self.logger.error(f"❌ [WAF Client] Network/timeout error: "
                                f"message={str(error)}, "
                                f"timeout={'ECONNABORTED' in str(error)}, "
                                f"isNetworkError={not hasattr(error, 'status')}")
                
            if not hasattr(error, 'status'):
                if config['onWafError'] == 'block' or config['blockOnError']:
                    return {
                        'allowed': False,
                        'blocked': True,
                        'reason': 'WAF_NETWORK_ERROR',
                        'message': 'Unable to connect to security service',
                        'error': {'type': 'NETWORK_ERROR', 'timeout': 'ECONNABORTED' in str(error)}
                    }
                
                return {
                    'allowed': True,
                    'blocked': False,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Security validation unavailable, request allowed',
                    'warning': True
                }
                
            if config['onWafError'] == 'block' or config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_UNEXPECTED_ERROR',
                    'message': 'Unexpected error during security validation',
                    'error': {'type': 'UNKNOWN', 'status': getattr(error, 'status', None)}
                }
                
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_UNEXPECTED_ERROR',
                'message': 'Security validation error, request allowed',
                'warning': True
            }
            
    def validate_request_sync(self, method: str, path: str, headers: Dict[str, str],
                            body: Any = None, query: Dict = None, params: Dict = None,
                            client_ip: str = 'unknown') -> Dict:
        """Sync version of request validation"""
        config = self.get_current_config()
        
        try:
                
            payload = {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body,
                'query': query or {},
                'params': params or {},
                'timestamp': datetime.now().isoformat(),
                'clientIp': client_ip,
                'userAgent': headers.get('user-agent', ''),
                
                # Send current protection settings to server - DYNAMIC
                'protections': config['protections'],
                
                'clientInfo': {
                    'apiKey': self.api_key,
                    'version': '2.1.0',
                    'responseType': config['responseType'],
                    'configFetchedAt': config.get('configFetchedAt'),
                    'configUpdatedAt': config.get('configUpdatedAt')
                }
            }
            
            if config['logRequests']:
                enabled_protections = [
                    name for name, prot_config in config['protections'].items()
                    if prot_config['enabled']
                ]
                config_age = None
                if config.get('configFetchedAt'):
                    config_age = str(int((time.time() - datetime.fromisoformat(config['configFetchedAt']).timestamp()))) + 's'
                
                self.logger.info(f"🔍 [WAF Client] Sending for validation: "
                               f"method={method}, path={path}, hasBody={bool(body)}, "
                               f"protections={enabled_protections}, ip={client_ip}, "
                               f"configAge={config_age or 'unknown'}")
                
            request_headers = {
                'Content-Type': 'application/json',
                'Authorization': self.api_key,
                'X-WAF-Client': 'python',
                'X-WAF-Response-Type': config['responseType'],
                **config['customHeaders']
            }
            
            response = requests.post(
                self.waf_endpoint,
                json=payload,
                headers=request_headers,
                timeout=config['timeout']
            )
            
            response_data = response.json()
            
            if config['logRequests']:
                applied_protections = []
                if 'appliedProtections' in response_data:
                    applied_protections = [
                        name for name, prot_config in response_data['appliedProtections'].items()
                        if prot_config.get('enabled', False)
                    ]
                    
                self.logger.info(f"📨 [WAF Client] Server response: "
                               f"status={response.status_code}, "
                               f"blocked={response_data.get('blocked', False)}, "
                               f"reason={response_data.get('reason')}, "
                               f"violations={response_data.get('validationResults', {}).get('totalViolations', 0)}, "
                               f"appliedProtections={applied_protections}")
            
            return response_data
            
        except requests.exceptions.Timeout:
            if config['logRequests']:
                self.logger.error("❌ [WAF Client] Network/timeout error: Timeout")
                
            if config['onWafError'] == 'block' or config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Unable to connect to security service',
                    'error': {'type': 'TIMEOUT', 'timeout': True}
                }
            
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_NETWORK_ERROR',
                'message': 'Security validation unavailable, request allowed',
                'warning': True
            }
            
        except Exception as error:
            if config['logRequests']:
                is_network_error = not hasattr(error, 'response')
                status = getattr(error, 'response', {}).get('status_code') if hasattr(error, 'response') else None
                self.logger.error(f"❌ [WAF Client] Network/timeout error: "
                                f"message={str(error)}, "
                                f"timeout={'timeout' in str(error).lower()}, "
                                f"status={status}, "
                                f"isNetworkError={is_network_error}")
                
            if not hasattr(error, 'response'):
                if config['onWafError'] == 'block' or config['blockOnError']:
                    return {
                        'allowed': False,
                        'blocked': True,
                        'reason': 'WAF_NETWORK_ERROR',
                        'message': 'Unable to connect to security service',
                        'error': {'type': 'NETWORK_ERROR', 'timeout': 'timeout' in str(error).lower()}
                    }
                
                return {
                    'allowed': True,
                    'blocked': False,
                    'reason': 'WAF_NETWORK_ERROR',
                    'message': 'Security validation unavailable, request allowed',
                    'warning': True
                }
                
            if hasattr(error, 'response') and hasattr(error.response, 'json'):
                try:
                    return error.response.json()
                except:
                    pass
                    
            if config['onWafError'] == 'block' or config['blockOnError']:
                return {
                    'allowed': False,
                    'blocked': True,
                    'reason': 'WAF_UNEXPECTED_ERROR',
                    'message': 'Unexpected error during security validation',
                    'error': {'type': 'UNKNOWN', 'status': getattr(error, 'response', {}).get('status_code')}
                }
                
            return {
                'allowed': True,
                'blocked': False,
                'reason': 'WAF_UNEXPECTED_ERROR',
                'message': 'Security validation error, request allowed',
                'warning': True
            }
            
    def create_graphql_error_response(self, operation_info: Optional[Dict], validation: Dict) -> Dict:
        """Create GraphQL response with detailed violation information"""
        def to_camel_case(s: str) -> str:
            if not s:
                return s
            return s[0].lower() + s[1:]
            
        # Include detailed violation information in GraphQL response
        violation_details = validation.get('validationResults', {}).get('violations', [])
        violation_summary = []
        
        for v in violation_details:
            violation_summary.append({
                'type': v.get('type', ''),
                'severity': v.get('severity', ''),
                'count': len(v.get('details', [])) if isinstance(v.get('details'), list) else 1,
                'readableType': v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
            })
            
        # Create human-readable violation list
        violation_list = ', '.join([
            v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
            for v in violation_details
        ])
        
        enhanced_message = f"{validation.get('message', 'Request blocked by security policy')} ({violation_list})" if violation_list else validation.get('message', 'Request blocked by security policy')
        
        if not operation_info:
            return {
                'data': None,
                'errors': [{
                    'message': enhanced_message,
                    'extensions': {
                        'code': validation.get('reason', 'SECURITY_VIOLATION'),
                        'blocked': True,
                        'waf': True,
                        'violations': violation_summary,
                        'violationTypes': violation_list,
                        'totalViolations': validation.get('validationResults', {}).get('totalViolations', 0),
                        'highSeverityViolations': validation.get('validationResults', {}).get('highSeverityViolations', 0)
                    }
                }]
            }
            
        operation_name = to_camel_case(operation_info.get('name', ''))
        response = {
            'data': {},
            'errors': [{
                'message': enhanced_message,
                'extensions': {
                    'code': validation.get('reason', 'SECURITY_VIOLATION'),
                    'operation': operation_name,
                    'blocked': True,
                    'waf': True,
                    'violations': violation_summary,
                    'violationTypes': violation_list,
                    'totalViolations': validation.get('validationResults', {}).get('totalViolations', 0),
                    'highSeverityViolations': validation.get('validationResults', {}).get('highSeverityViolations', 0)
                }
            }]
        }
        
        response['data'][operation_name] = {
            'success': False,
            'message': enhanced_message,
            'blocked': True,
            'reason': validation.get('reason'),
            'violations': violation_list,
            'violationDetails': violation_summary
        }
        
        return response
        
    def parse_graphql_operation(self, body: Any) -> Optional[Dict]:
        """Extract GraphQL operation info"""
        try:
            if not body or not isinstance(body, dict) or 'query' not in body:
                return None
                
            operation_name = body.get('operationName') or self.extract_operation_name_from_query(body['query'])
            return {'name': operation_name} if operation_name else None
            
        except Exception:
            return None
            
    def extract_operation_name_from_query(self, query: str) -> Optional[str]:
        """Extract operation name from GraphQL query"""
        try:
            match = re.search(r'(query|mutation|subscription)\s+(\w+)', query, re.IGNORECASE)
            return match.group(2) if match else None
        except Exception:
            return None
            
    def get_config_summary(self) -> Dict:
        """Get current configuration summary"""
        config = self.get_current_config()
        enabled_protections = [
            name for name, prot_config in config['protections'].items()
            if prot_config['enabled']
        ]
        
        disabled_protections = [
            name for name, prot_config in config['protections'].items()
            if not prot_config['enabled']
        ]
        
        config_age = None
        if config.get('configFetchedAt'):
            config_age = int((time.time() - datetime.fromisoformat(config['configFetchedAt']).timestamp()))
        
        return {
            'enabled': config['enabled'],
            'responseType': config['responseType'],
            'enabledProtections': enabled_protections,
            'disabledProtections': disabled_protections,
            'totalProtections': len(config['protections']),
            'cacheEnabled': config['enableCache'],
            'validatedMethods': config['validatedMethods'],
            'ignoredPaths': config['ignoredPaths'],
            'configSource': 'api' if self.config_cache else 'fallback',
            'configAge': config_age,
            'lastConfigUpdate': config.get('configUpdatedAt'),
            'refreshInterval': str(self.config_refresh_interval) + 's',
            'discoveredProtections': sorted(list(self.discovered_protections)) if self.discovered_protections else []
        }
        
    # Flask middleware
    def flask_middleware(self):
        """Flask middleware implementation"""
        self.start_cache_cleaner()
        
        if self.get_current_config()['logRequests']:
            config_summary = self.get_config_summary()
            self.logger.info(f"🛡️  [WAF Client] WAF Client initialized with config: {config_summary}")
            
        def middleware():
            config = self.get_current_config()
            
            if not config['enabled']:
                return None
                
            path = request.path
            method = request.method
            
            if self.should_ignore_path(path):
                if config['logRequests']:
                    self.logger.info(f"⏭️  [WAF Client] Ignoring path: {path}")
                return None
                
            if not self.should_validate_method(method):
                if config['logRequests']:
                    self.logger.info(f"⏭️  [WAF Client] Ignoring method: {method}")
                return None
                
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                          request.environ.get('HTTP_X_REAL_IP', 
                                                            request.environ.get('REMOTE_ADDR', 'unknown')))
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
                
            # Create request hash for caching
            body = None
            try:
                if request.is_json:
                    body = request.get_json()
                elif request.form:
                    body = dict(request.form)
            except Exception:
                pass
                
            request_hash = self.create_request_hash(method, path, body, dict(request.headers))
            cached_result = self.check_cache(request_hash)
            
            if cached_result:
                if config['logRequests']:
                    self.logger.info('📋 [WAF Client] Using cached result')
                    
                if not cached_result.get('allowed', True) or cached_result.get('blocked', False):
                    if config['responseType'] == 'graphql':
                        operation_info = self.parse_graphql_operation(body)
                        graphql_response = self.create_graphql_error_response(operation_info, cached_result)
                        return jsonify(graphql_response), 200
                    else:
                        # Enhanced cached response with violation details
                        violation_details = cached_result.get('validationResults', {}).get('violations', [])
                        violation_summary = ', '.join([
                            v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                            for v in violation_details
                        ])
                        
                        enhanced_message = f"{cached_result.get('message', '')} ({violation_summary})" if violation_summary else cached_result.get('message', '')
                        
                        return jsonify({
                            'success': False,
                            'blocked': True,
                            'reason': cached_result.get('reason'),
                            'message': enhanced_message,
                            'violations': violation_summary,
                            'details': cached_result.get('validationResults'),
                            'cached': True
                        }), 403
                        
                return None
                
            # Validate request
            validation = self.validate_request_sync(
                method, path, dict(request.headers), body,
                dict(request.args), {}, client_ip
            )
            
            self.save_to_cache(request_hash, validation)
            
            if not validation.get('allowed', True) or validation.get('blocked', False):
                # Enhanced logging with detailed violation information
                if config['logRequests']:
                    violation_details = validation.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        f"{v.get('type', '').replace('_DETECTED', '').replace('_', ' ')} ({len(v.get('details', [])) if isinstance(v.get('details'), list) else 1})"
                        for v in violation_details
                    ])
                    
                    high_severity = len([v for v in violation_details if v.get('severity') in ['CRITICAL', 'HIGH']])
                    
                    self.logger.info(f"🚫 [WAF Client] Request blocked: "
                                   f"reason={validation.get('reason')}, "
                                   f"violations={validation.get('validationResults', {}).get('totalViolations', 0)}, "
                                   f"types={violation_summary or 'Unknown'}, "
                                   f"severity={high_severity} high/critical")
                    
                    if violation_details:
                        self.logger.info('🔍 [WAF Client] Violation details:')
                        for i, violation in enumerate(violation_details, 1):
                            details_count = len(violation.get('details', [])) if isinstance(violation.get('details'), list) else 'N/A'
                            self.logger.info(f"  {i}. {violation.get('type')} ({violation.get('severity')}): {details_count} instances")
                    
                if config['responseType'] == 'graphql':
                    operation_info = self.parse_graphql_operation(body)
                    graphql_response = self.create_graphql_error_response(operation_info, validation)
                    return jsonify(graphql_response), 200
                else:
                    # Enhanced REST response with human-readable violation summary
                    violation_details = validation.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                        for v in violation_details
                    ])
                    
                    enhanced_message = f"{validation.get('message', '')} ({violation_summary})" if violation_summary else validation.get('message', '')
                    
                    return jsonify({
                        'success': False,
                        'blocked': True,
                        'reason': validation.get('reason'),
                        'message': enhanced_message,
                        'violations': violation_summary,
                        'details': validation.get('validationResults')
                    }), 403
                    
            if config['logRequests']:
                self.logger.info('✅ [WAF Client] Request approved')
                
            return None
            
        return middleware
        
    # FastAPI middleware
    async def fastapi_middleware(self, request: Request, call_next):
        """FastAPI middleware implementation"""
        config = self.get_current_config()
        
        if not config['enabled']:
            response = await call_next(request)
            return response
            
        path = request.url.path
        method = request.method
        
        if self.should_ignore_path(path):
            if config['logRequests']:
                self.logger.info(f"⏭️  [WAF Client] Ignoring path: {path}")
            response = await call_next(request)
            return response
            
        if not self.should_validate_method(method):
            if config['logRequests']:
                self.logger.info(f"⏭️  [WAF Client] Ignoring method: {method}")
            response = await call_next(request)
            return response
            
        # Get client IP
        client_ip = request.client.host if request.client else 'unknown'
        if 'x-forwarded-for' in request.headers:
            forwarded_ips = request.headers['x-forwarded-for'].split(',')
            client_ip = forwarded_ips[0].strip()
        elif 'x-real-ip' in request.headers:
            client_ip = request.headers['x-real-ip']
            
        # Get request body
        body = None
        try:
            if request.headers.get('content-type', '').startswith('application/json'):
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes.decode())
        except Exception:
            pass
            
        # Create request hash for caching
        request_hash = self.create_request_hash(method, path, body, dict(request.headers))
        cached_result = self.check_cache(request_hash)
        
        if cached_result:
            if config['logRequests']:
                self.logger.info('📋 [WAF Client] Using cached result')
                
            if not cached_result.get('allowed', True) or cached_result.get('blocked', False):
                if config['responseType'] == 'graphql':
                    operation_info = self.parse_graphql_operation(body)
                    graphql_response = self.create_graphql_error_response(operation_info, cached_result)
                    return JSONResponse(content=graphql_response, status_code=200)
                else:
                    # Enhanced cached response with violation details
                    violation_details = cached_result.get('validationResults', {}).get('violations', [])
                    violation_summary = ', '.join([
                        v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                        for v in violation_details
                    ])
                    
                    enhanced_message = f"{cached_result.get('message', '')} ({violation_summary})" if violation_summary else cached_result.get('message', '')
                    
                    return JSONResponse({
                        'success': False,
                        'blocked': True,
                        'reason': cached_result.get('reason'),
                        'message': enhanced_message,
                        'violations': violation_summary,
                        'details': cached_result.get('validationResults'),
                        'cached': True
                    }, status_code=403)
                    
        # Validate request
        validation = await self.validate_request_async(
            method, path, dict(request.headers), body,
            dict(request.query_params), {}, client_ip
        )
        
        self.save_to_cache(request_hash, validation)
        
        if not validation.get('allowed', True) or validation.get('blocked', False):
            # Enhanced logging with detailed violation information
            if config['logRequests']:
                violation_details = validation.get('validationResults', {}).get('violations', [])
                violation_summary = ', '.join([
                    f"{v.get('type', '').replace('_DETECTED', '').replace('_', ' ')} ({len(v.get('details', [])) if isinstance(v.get('details'), list) else 1})"
                    for v in violation_details
                ])
                
                high_severity = len([v for v in violation_details if v.get('severity') in ['CRITICAL', 'HIGH']])
                
                self.logger.info(f"🚫 [WAF Client] Request blocked: "
                               f"reason={validation.get('reason')}, "
                               f"violations={validation.get('validationResults', {}).get('totalViolations', 0)}, "
                               f"types={violation_summary or 'Unknown'}, "
                               f"severity={high_severity} high/critical")
                
                if violation_details:
                    self.logger.info('🔍 [WAF Client] Violation details:')
                    for i, violation in enumerate(violation_details, 1):
                        details_count = len(violation.get('details', [])) if isinstance(violation.get('details'), list) else 'N/A'
                        self.logger.info(f"  {i}. {violation.get('type')} ({violation.get('severity')}): {details_count} instances")
                
            if config['responseType'] == 'graphql':
                operation_info = self.parse_graphql_operation(body)
                graphql_response = self.create_graphql_error_response(operation_info, validation)
                return JSONResponse(content=graphql_response, status_code=200)
            else:
                # Enhanced REST response with human-readable violation summary
                violation_details = validation.get('validationResults', {}).get('violations', [])
                violation_summary = ', '.join([
                    v.get('type', '').replace('_DETECTED', '').replace('_', ' ')
                    for v in violation_details
                ])
                
                enhanced_message = f"{validation.get('message', '')} ({violation_summary})" if violation_summary else validation.get('message', '')
                
                return JSONResponse({
                    'success': False,
                    'blocked': True,
                    'reason': validation.get('reason'),
                    'message': enhanced_message,
                    'violations': violation_summary,
                    'details': validation.get('validationResults')
                }, status_code=403)
                
        if config['logRequests']:
            self.logger.info('✅ [WAF Client] Request approved')
            
        response = await call_next(request)
        return response
        
    # Cleanup method to stop intervals when shutting down
    def destroy(self):
        """Cleanup method to stop intervals and clear caches"""
        self._stop_config_update_loop()
        self.cache.clear()
        self.rate_limit_map.clear()
        
        config = self.get_current_config()
        if config['logRequests']:
            self.logger.info('🛑 [WAF Client] Client destroyed and cleaned up')


# Example usage with Flask - COMPLETELY DYNAMIC
def create_flask_app_with_waf():
    """Example of how to use WAF Client with Flask - NO hardcoded protections"""
    from flask import Flask
    
    app = Flask(__name__)
    
    # Initialize WAF Client - NO hardcoded protection names
    waf_client = WAFClient({
        'apiKey': 'your-api-key-here',
        'logRequests': True,
        'responseType': 'rest',  # or 'graphql'
        # NO protections defined - will be fetched dynamically from API
    })
    
    # Register middleware
    @app.before_request
    def waf_middleware():
        return waf_client.flask_middleware()()
    
    @app.route('/api/test', methods=['POST'])
    def test_endpoint():
        return jsonify({'message': 'Request passed WAF validation'})
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    @app.route('/waf/config')
    def waf_config():
        return jsonify(waf_client.get_config_summary())
    
    @app.route('/waf/protections')
    def waf_protections():
        """Show all discovered protections"""
        config = waf_client.get_current_config()
        return jsonify({
            'protections': config['protections'],
            'discoveredProtections': sorted(list(waf_client.discovered_protections)),
            'enabledCount': len([p for p, c in config['protections'].items() if c['enabled']]),
            'totalCount': len(config['protections'])
        })
    
    return app


# Example usage with FastAPI - COMPLETELY DYNAMIC  
def create_fastapi_app_with_waf():
    """Example of how to use WAF Client with FastAPI - NO hardcoded protections"""
    from fastapi import FastAPI
    from starlette.middleware.base import BaseHTTPMiddleware
    
    app = FastAPI()
    
    # Initialize WAF Client - NO hardcoded protection names
    waf_client = WAFClient({
        'apiKey': 'your-api-key-here',
        'logRequests': True,
        'responseType': 'rest',  # or 'graphql'
        # NO protections defined - will be fetched dynamically from API
    })
    
    # Add WAF middleware
    app.add_middleware(BaseHTTPMiddleware, dispatch=waf_client.fastapi_middleware)
    
    @app.post('/api/test')
    async def test_endpoint():
        return {'message': 'Request passed WAF validation'}
    
    @app.get('/health')
    async def health():
        return {'status': 'healthy'}
    
    @app.get('/waf/config')
    async def waf_config():
        return waf_client.get_config_summary()
    
    @app.get('/waf/protections')
    async def waf_protections():
        """Show all discovered protections"""
        config = waf_client.get_current_config()
        return {
            'protections': config['protections'],
            'discoveredProtections': sorted(list(waf_client.discovered_protections)),
            'enabledCount': len([p for p, c in config['protections'].items() if c['enabled']]),
            'totalCount': len(config['protections'])
        }
    
    return app
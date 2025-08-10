from setuptools import setup, find_packages

setup(
    name='netfend-waf-client',
    version='2.0.0',  # 👈 aumente a versão!
    description='WAF Client SDK for Python - Netfend',
    author='Seu Nome',
    author_email='support@netfend.emailsbit.com',
    url='https://github.com/Shieldhaus/netfend_waf_client',
    packages=find_packages(),  # 👈 isso é essencial
    install_requires=[
        'aiohttp',
        'fastapi',
        'flask',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)

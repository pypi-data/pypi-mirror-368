from setuptools import setup

setup(
    name='glimps-audit-cli',
    version='1.0.0',
    py_modules=['glimps_audit_client', 'glimps_audit_cli'],
    install_requires=[
        'requests>=2.28.0',
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'glimps-audit=glimps_audit_cli:cli',
        ],
    },
)

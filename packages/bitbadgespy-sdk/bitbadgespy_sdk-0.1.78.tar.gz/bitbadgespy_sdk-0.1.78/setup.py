from setuptools import setup, find_packages

setup(
    name="bitbadgespy-sdk",
    version="0.1.78",
    packages=find_packages(),
    install_requires=[
        "urllib3>=1.25.3",
        "python-dateutil",
        "requests>=2.0.0",
        "pydantic>=2.0.0"
    ],
)

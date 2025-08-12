from setuptools import setup, find_packages

setup(
    name="teams-alerter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-cloud-logging",
        "google-cloud-pubsub",
    ],
)

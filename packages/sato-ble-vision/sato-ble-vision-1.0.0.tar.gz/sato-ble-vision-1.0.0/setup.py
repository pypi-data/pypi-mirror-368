from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="sato-ble-vision",
    version="1.0.0",
    author="Dylan Barnett",
    author_email="dylanbarnett99@gmail.com", 
    description="MQTT Broker Control and IoT Data Management Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dylanbarnett99/sato-ble",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "paho-mqtt>=1.6.0",
        "pandas>=1.3.0",
        "psutil>=5.8.0",
        "requests>=2.25.0",
    ],
    package_data={
        "sato_ble_vision": [
            "pics/*.png",
            "templates/*.json",
        ],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "sato-ble-vision=sato_ble_vision.main:main",
        ],
    },
    keywords="mqtt, iot, broker, data, management",
    project_urls={
        "Bug Reports": "https://github.com/dylanbarnett99/sato-ble/issues",
        "Source": "https://github.com/dylanbarnett99/sato-ble",
    },
)

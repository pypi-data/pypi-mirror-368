from setuptools import setup, find_packages

setup(
    name="shared-utils-ems",
    version="4.1.1",
    packages=find_packages(),
    install_requires=[],  
    description="A shared utility library for event management system based on microservices architecture.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="iman sadati",
    author_email="iman.3adati@gmail.com",
    url="https://github.com/imansadati/event_management_system",  # Optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
from setuptools import find_packages, setup

setup(
    name="django-admin-models-search",
    version="1.0.1",
    description="Add a search bar for registered models in Django admin",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Timothée Roy",
    author_email="timothee@vingtcinq.io",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    where=".",
)

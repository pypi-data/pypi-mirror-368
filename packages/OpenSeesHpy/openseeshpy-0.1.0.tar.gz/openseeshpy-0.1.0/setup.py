from setuptools import setup, find_packages

setup(
    name="OpenSeesHpy",
    version="0.1.0",
    author="OpesnSeesHouse",
    author_email="OpenSeesHouse@gmail.com",
    description="an OpenSees customization optimized for performance-based analysis and design of structures",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://openseeshouse.com/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
        package_data={
        "OpenSeesHpy": ["*.pyd"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires="==3.13",
    project_urls={
        "Source": "https://github.com/OpenSeesHouse/OpenSeesH",
    },
    include_package_data=True,
)

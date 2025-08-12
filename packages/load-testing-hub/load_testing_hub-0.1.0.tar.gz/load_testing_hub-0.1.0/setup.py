from setuptools import setup, find_packages

setup(
    name="load-testing-hub",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "httpx",
        "pyyaml>=6.0.2",
        "pydantic>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'load-testing-hub = load_testing_hub.cli.main:cli',
        ],
    },
    author="Nikita Filonov",
    author_email="filonov.nikitkaa@gmail.com",
    description="""
    Python connector and CLI tool for uploading Locust performance 
    test reports to the Load Testing Hub API
    """,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nikita-Filonov/load-testing-hub",
    project_urls={
        "Bug Tracker": "https://github.com/Nikita-Filonov/load-testing-hub/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)

from setuptools import find_packages, setup

setup(
    name="pyvetic",
    version="0.34.0",
    description="Internal package for common utils",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vetic",
    author_email="techadmin@vetic.in",
    url="https://github.com/vetic-in/pyvetic",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-logging-loki>=0.3.0",
        "prometheus_client>=0.20.0",
        "psutil>=7.0.0",
    ],
    extras_require={
        "fastapi": ["fastapi>=0.90.0", "uvicorn"],
        "django": ["Django>=3.2"],
    },
    python_requires=">=3.8,<3.13",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)

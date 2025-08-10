from setuptools import setup, find_packages

setup(
    name="cpy",
    version="0.1.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "setuptools>=70.3.0",
        "deprecated",
        "cryptography>=45.0.4",
        "pyrogram",
        "tgcrypto",
        "requests",
        "fusepy",
        "async-upnp-client",
        "aiohttp",
        "defusedxml",
    ],
    entry_points={
        'console_scripts': [
            'ccrypt = cpy.ccrypt.cli:main',
            't3 = cpy.t3.cli:main',
            'dlnap = cpy.dlnap.cli:main',
        ],
    },
    author="CHARZ",
    author_email="your.email@example.com",
    description="Charz Python Library",
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)

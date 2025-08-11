import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tboxsdk",
    version="0.0.7",
    author="久知",
    author_email="haoxuan.yhx@antgroup.com",
    description="Common functions to interact with Tbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.alipay.com/ai_release/tboxsdk-python",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "httpx",
        "sseclient-py",
    ]
)

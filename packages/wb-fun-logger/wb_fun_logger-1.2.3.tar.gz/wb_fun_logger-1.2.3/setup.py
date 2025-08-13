from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wb_fun_logger",
    version="1.2.3",
    author="Guan Xingjian",
    author_email="guanxj99@outlook.com",
    description="A tool for logging function and send message to webhook robot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"}, 
    packages=find_packages(where="src"),
    install_requires=[
        "certifi",
        "charset-normalizer",
        "idna",
        "loguru",
        "python-dotenv",
        "PyYAML",
        "requests",
        "urllib3"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
    include_package_data=True
)

from setuptools import setup, find_packages
from pathlib import Path

# 读取README内容作为长描述
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="python-cnb",
    version="0.7.0",
    author="Tencent Cloud",
    author_email="ericdduan@tencent.com",
    description="CNB OpenAPI的Python SDK,方便与CNB平台进行交互",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cnb.cool",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "python-dotenv>=0.21.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://cnb.cool/cnb/sdk/python-cnb",
        "Documentation": "https://docs.cnb.cool",
    },
)
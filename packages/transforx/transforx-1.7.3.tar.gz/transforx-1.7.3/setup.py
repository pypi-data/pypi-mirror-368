from setuptools import setup, find_packages

setup(
    name="transforx",
    version="1.7.3",
    author="Ali-Jafari",
    author_email="thealiapi@gmail.com",
    description="A simple Python translation library using Google Translate.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iTs-GoJo/TransforX",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.6",
)

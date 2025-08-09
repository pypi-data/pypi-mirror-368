from setuptools import setup, find_packages

setup(
    name="py2mermaid",
    version="0.1.0",
    author="raghuvasanthrao",
    author_email="k.s.raghuvsanthrao@gmail.com",
    description="A Python helper library to create Mermaid.js diagrams",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/raghuvasanthrao/mermaidpy",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)

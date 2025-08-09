from setuptools import setup, find_packages

setup(
    name="seanox_ai_nlp",
    version="1.0.0",
    packages=find_packages(),
    author="Seanox Software Solutions",
    description=(
        "Lightweight NLP components for semantic processing of domain-specific content."
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seanox/seanox-ai-nlp",
    license="Apache-2.0",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent"
    ],
    keywords=[
        "NLP", "semantic", "units", "domain-specific", "text processing", "information extraction"
    ],
)

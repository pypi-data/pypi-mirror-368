from setuptools import setup, find_packages

setup(
    name="text_diff_engine",
    version="3.0.1",
    description="A Python wrapper for the Text Diff Engine with block moves API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Franciszek Łąjszczak",
    author_email="franciszek@formamind.com",
    url="https://www.formamind.com/en/diffEngine",  # Replace with your repository URL if available
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

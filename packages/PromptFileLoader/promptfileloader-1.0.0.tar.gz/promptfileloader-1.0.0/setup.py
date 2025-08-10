from setuptools import setup, find_packages

setup(
    name="PromptFileLoader",
    version="1.0.0",
    author="Akashh Krishh",
    author_email="akashhkrishh@gmail.com",
    description="A simple prompt loader supporting YAML and TXT files with caching",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/akashhkrishh/PromptFileLoader",  # update with your repo URL
    packages=find_packages(),
    install_requires=["PyYAML"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vibeisodd",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered odd number detection using GPT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/VibeIsOdd",
    packages=setuptools.find_packages(),
    install_requires=[
        "openai>=1.0.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    keywords="ai gpt numbers odd detection parody",
    include_package_data=True,
    package_data={"": ["LICENSE"]},
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/VibeIsOdd/issues",
    },
)

from setuptools import setup, find_packages

setup(
    name="tucker-trucker",
    version="0.1.0",
    description="A Boston Terrier delivery game built with pygame.",
    author="Jerem Evans",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.6.0"
    ],
    entry_points={
        "console_scripts": [
            "tucker-trucker=main:main"
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.wav", "*.ogg", "*.mp3"]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
    ],
    long_description=open("README.md", encoding="utf-8").read() if __import__('os').path.exists("README.md") else "",
    long_description_content_type="text/markdown",
)

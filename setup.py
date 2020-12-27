import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mergecat",
    version="0.0.7",
    author="Ian Moore",
    author_email="exsnap@yttr.org",
    description="Automate the downloading of Snapchat memories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yttrian/exsnap",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "exsnap = exsnap.__main__:exsnap"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "click",
        "aiohttp",
        "alive-progress"
    ]
)

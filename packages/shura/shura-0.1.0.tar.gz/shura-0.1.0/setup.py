from setuptools import setup, find_packages

setup(
    name="shura",
    version="0.1.0",
    author="Guy Shaul",
    author_email= "guyshaul8@gmail.com",
    url="https://github.com/guy-shaul/shura",
    description="Elegant, colored, plug-and-play logging for Python",
    packages=find_packages(),
    install_requires=["colorama"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

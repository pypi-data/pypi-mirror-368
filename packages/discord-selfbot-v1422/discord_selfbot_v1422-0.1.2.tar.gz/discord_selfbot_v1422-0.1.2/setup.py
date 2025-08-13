from setuptools import setup, find_packages

setup(
    name="discord-selfbot-v1422",          # Your package name on PyPI
    version="0.1.2",                 # Version number
    author="auth",
    author_email="bisects@proton.me",
    description="wrd",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["package", "package.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


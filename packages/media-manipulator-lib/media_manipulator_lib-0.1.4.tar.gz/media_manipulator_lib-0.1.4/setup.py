from setuptools import setup, find_packages

setup(
    name="media-manipulator-lib",
    version="0.1.4",
    author="Aditya Sharma",
    author_email="aditya.3sharma@angelone.in",
    description="A composable FFmpeg-based video editing library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "ffmpeg-python",
        "colorlog",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

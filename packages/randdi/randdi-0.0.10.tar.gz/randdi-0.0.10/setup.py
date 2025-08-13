from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.10'
DESCRIPTION = 'fucking bitch'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'

# Setting up
setup(
    name="randdi",
    version=VERSION,
    author="syed",
    author_email="syedadil093@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

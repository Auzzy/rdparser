from setuptools import setup

setup(
    name='rdparser',
    version='1.0',
    install_requires=[
        "beautifulsoup4 >= 4.8.1",
        "requests >= 2.22.0",
        "lxml >= 4.4.2",
        "zope.testbrowser >= 5.3.3"
    ],
    author="Austin Noto-Moniz",
    author_email="metalnut4@netscape.net",
    packages=['rdparserlib'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)

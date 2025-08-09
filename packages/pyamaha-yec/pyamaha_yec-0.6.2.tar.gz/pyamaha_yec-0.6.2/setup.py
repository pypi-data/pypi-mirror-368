from setuptools import setup

setup(
    name="pyamaha-yec",
    packages=["pyamaha"],
    version="0.6.2",
    description="Python implementation of Yamaha Extended Control API Specification.",
    author="Jack Powell",
    author_email="jack.powell@gmail.com",
    url="https://github.com/jackjpowell/pyamaha",
    download_url="https://github.com/jackjpowell/pyamaha/releases/tag/0.4",
    keywords=["Yamaha", "API", "Yamaha Extended Control"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "requests",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    extras_require={"async": ["aiohttp"]},
)

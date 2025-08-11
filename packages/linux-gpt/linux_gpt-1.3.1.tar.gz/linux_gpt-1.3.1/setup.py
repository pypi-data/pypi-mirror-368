from setuptools import setup, find_packages

setup(
    name="linux-gpt",
    version="1.3.1",
    description="An elite terminal-based assistant for Linux developers, security engineers, and ethical hackers.",
    author="AmianDevSec",
    author_email="amiandevsec@gmail.com",
    url="https://github.com/AmianDevSec/lgpt",
    license="GPL-3.0-only",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv",
        "packaging",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "lgpt=lgpt.lgpt:main",
        ],
    },
    package_data={
        "lgpt": [".env"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
)

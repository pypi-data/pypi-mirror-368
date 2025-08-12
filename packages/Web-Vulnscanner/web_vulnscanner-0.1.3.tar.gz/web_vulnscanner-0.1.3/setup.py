from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="Web_Vulnscanner",                         # PyPI project name (can keep)
    version="0.1.3",                                # bump this
    py_modules=["cli", "main"],                     # top-level modules
    packages=find_packages(include=["scanners*", "extras*"]),
    install_requires=[
        "playwright>=1.42.0",
        "httpx>=0.27.0",
        "requests>=2.31.0",
        "h2>=4.1.0",
        "rich>=13.0.0",
    ],
    author="Randomguy",
    author_email="gawzenneth@gmail.com",
    description="A Simple CLI python tool to scan a website for common vulns.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/randomguy6407/Vulnscanner",
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "web-vulnscanner=cli:main",   # user types `web-vulnscanner`
        ],
    },
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discord.py-webhook",
    version="1.0.0",
    author="7",
    author_email="jj9dptr57@mozmail.com",
    description="A powerful Discord webhook library with extensive customization options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/7vntii/discord.py-webhook",
    project_urls={
        "Bug Tracker": "https://github.com/7vntii/discord.py-webhook/issues",
        "Documentation": "https://github.com/7vntii/discord.py-webhook",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="discord, webhook, bot, api, messaging",
    include_package_data=True,
    zip_safe=False,
)

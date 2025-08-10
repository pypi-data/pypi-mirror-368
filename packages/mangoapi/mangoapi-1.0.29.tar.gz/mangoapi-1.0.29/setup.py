from setuptools import setup, find_packages
import re

def version():
    filename = "mango/__init__.py"
    with open(filename) as f:
        match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""", f.read(), re.M)
    if not match:
        raise RuntimeError("{} doesn't contain __version__".format(filename))
    version = match.groups()[0]
    return version
with open("README.md", encoding="utf8") as readme:
    long_desc = readme.read()


# Setting up
setup(
    name="mangoapi",
    version=version(),
    author="Mishal",
    author_email="mishel@gmail.temb",
    description="Python Wrapper For MangiAPI",
    long_description_content_type="text/markdown",
    long_description=long_desc,
    packages=find_packages(),
    license="MIT",
    url="https://github.com/Mishel-07/MangoAPI",
    download_url="https://github.com/Mishel-07/MangoAPI/blob/main/README.md",
    install_requires=["httpx"],
    keywords="PYTHON, MANGOAPI, LLM, image generation, art, ai",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    project_urls={
        "Tracker": "https://github.com/Mishel-07/MangoAPI/issues",
        "Community": "https://t.me/XBOTSUPPORTS",
        "Source": "https://github.com/Mishel-07/MangoAPI",
    },
    python_requires="~=3.7",
)

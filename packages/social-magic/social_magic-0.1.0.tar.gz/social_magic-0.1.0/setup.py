from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="social-magic",
    version="0.1.0",
    author="SocialMagic Team",
    author_email="contact@socialmagic.dev",
    description="A Python library for social media content enhancement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/socialmagic/social-magic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="sentiment analysis, image detection, story generation, social media",
    project_urls={
        "Bug Reports": "https://github.com/socialmagic/social-magic/issues",
        "Source": "https://github.com/socialmagic/social-magic",
        "Documentation": "https://github.com/socialmagic/social-magic#readme",
    },
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-bsv-integration",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Django integration for BSV blockchain using py-bsv SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/django-bsv-integration",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "bsv-sdk",
        "whatsonchain>=0.0.3", 
        "yenpoint_1satordinals",
        "aiohttp>=3.8.0",
        "requests>=2.25.0",
        "Pillow>=8.0.0",
        "python-magic>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "flake8",
            "isort",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent

long_description = "BlockBee checkout backend for django-payments"
readme_path = BASE_DIR / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="django-payments-blockbee",
    version="1.0.3",
    description="BlockBee Checkout backend for django-payments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BlockBee",
    author_email="support@blockbee.io",
    url="https://github.com/blockbee-io/django-payments-blockbee",
    project_urls={
        "Homepage": "https://github.com/blockbee-io/django-payments-blockbee",
        "Source": "https://github.com/blockbee-io/django-payments-blockbee",
        "Tracker": "https://github.com/blockbee-io/django-payments-blockbee/issues",
    },
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "django>=3.2",
        "django-payments>=2.0",
        "requests>=2.25",
        "python-blockbee>=2.1.1",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["django", "payments", "django-payments", "blockbee", "crypto", "checkout"],
)
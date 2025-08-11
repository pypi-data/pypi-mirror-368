from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-db-s3-backup",
    version="0.1.3",
    author="Otu Taofeeq",
    author_email="otutaofeeqi@gmail.com",
    description="Django database backup with S3 storage and scheduling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Taofeeq97/postgreSQL_backup.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Django>=3.2",
        "boto3>=1.26.0",
        "django-apscheduler>=0.6.2",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-django>=4.5.0',
            'coverage>=6.0',
        ],
    },
    keywords="django database backup s3_access",
)
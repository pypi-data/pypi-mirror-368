from setuptools import setup, find_packages

setup(
    name="mercury-orm",
    version="v0.6.2",
    description="ORM for Custom Objects de Zendesk",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pedro Andrade",
    author_email="pedro.moisesandrade@gmail.com",
    url="https://github.com/BCR-CX/mercury-orm",
    project_urls={
        "Homepage": "https://github.com/BCR-CX/mercury-orm",
        "Issues": "https://github.com/BCR-CX/mercury-orm/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "Unidecode==1.3.8",
    ],
    license="MIT",
    packages=find_packages(),
)

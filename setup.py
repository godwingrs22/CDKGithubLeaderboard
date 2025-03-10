import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="cdk-github-leaderboard",
    version="0.1.0",
    description="CDK Github Leaderboard Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    packages=setuptools.find_packages(),
    install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "pandas>=1.3.0"
    ],
    python_requires=">=3.9",
)

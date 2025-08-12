from setuptools import setup, find_packages

# Read README.md as UTF-8
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="matrixchain",
    version="0.1.0",
    author="Chauhan Pruthviraj",
    author_email="chauhanpruthviraj309@gmail.com",
    description="Matrix Chain Multiplication with table printing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
)

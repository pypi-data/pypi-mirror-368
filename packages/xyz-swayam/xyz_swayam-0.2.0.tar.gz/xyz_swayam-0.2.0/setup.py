from setuptools import setup, find_packages

setup(
    name="xyz-swayam",  # Change to your unique package name
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "xyz": ["sample.pdf"],
    },
    install_requires=[],
    author="Your Name",
    author_email="your@email.com",
    description="A test package with a PDF",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Optional
    python_requires=">=3.6",
)

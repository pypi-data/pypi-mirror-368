from setuptools import setup, find_packages

setup(
    name="imagecolorclassifier",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless>=4.5.0",
        "numpy>=1.19.0"
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)

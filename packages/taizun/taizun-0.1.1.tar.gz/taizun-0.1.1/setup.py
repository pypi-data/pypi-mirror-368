from setuptools import setup, find_packages

setup(
    name="taizun",
    version="0.1.1", 
    author="Taizun", 
    author_email="taizun8@gmail.com", 
    description="A Python library for simplifying tasks and enhancing generative AI workflows.",  # Short description
    long_description=open("README.md").read(),  # Use README.md as the long description
    long_description_content_type="text/markdown", 
    url="https://github.com/t4zn/taizun", 
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
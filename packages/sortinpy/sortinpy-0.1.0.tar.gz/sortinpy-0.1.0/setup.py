from setuptools import setup, find_packages

setup(
    name="sortinpy",
    version="0.1.0",
    author="wandsondev",
    author_email="wandsondev@gmail.com",
    description="Pacote Python com vários algoritmos de ordenação e busca",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="",  # pode colocar link do github depois, se quiser
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


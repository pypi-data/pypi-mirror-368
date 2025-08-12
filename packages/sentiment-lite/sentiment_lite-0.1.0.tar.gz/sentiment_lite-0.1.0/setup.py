from setuptools import setup, find_packages

setup(
    name="sentiment-lite",
    version="0.1.0",
    author="Divya Athalye",
    author_email="divya.athalye@gmail.com",
    description="A simple lexicon-based sentiment analysis tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sentiment-lite",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires='>=3.6',
)

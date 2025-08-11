from setuptools import setup , find_packages

with open("README.md","r") as file:
    readme = file.read()

setup(
    name="Aiology",
    version="0.0.6",
    author="Seyed Moied Seyedi (Single Star)",
    packages=find_packages(),
    install_requires=[
        "pypdf","arabic-reshaper","python-bidi","setuptools","chromadb==0.4.14","colorama","SpeechRecognition==3.14.3","faster_whisper==1.1.1"
    ],
    license="MIT",
    description="Ai library",
    long_description=readme,
    long_description_content_type="text/markdown"
)
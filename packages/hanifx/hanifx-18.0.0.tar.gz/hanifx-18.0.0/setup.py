from setuptools import setup, find_packages

long_description = """
HanifX is an innovative Python code encoder designed to protect your source code by converting it 
into a unique, emoji-based obfuscated format combined with a custom shuffled symbol set.

Ideal for developers who want to securely share their Python scripts on platforms like GitHub without 
exposing the original source code. HanifX ensures your code runs flawlessly after encoding and decoding.

Features:
- Emoji tokenizer for Python keywords for added security and uniqueness.
- Extensive symbol set including emojis and special characters.
- Key-driven symbol shuffling to produce distinct encoded outputs.
- Auto-executing encoded scripts with zero errors.
- Simple API supporting string and file encoding.

Protect your Python code effortlessly with HanifX — where security meets creativity.
"""

setup(
    name="hanifx",
    version="18.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="Secure and creative Python code encoder using emojis and custom symbols",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540/hanifx",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="python encoder emoji obfuscation security hanifx",
    project_urls={
        "Source": "https://github.com/hanifx-540/hanifx",
        "Facebook": "https://facebook.com/hanifx540",
    }
)

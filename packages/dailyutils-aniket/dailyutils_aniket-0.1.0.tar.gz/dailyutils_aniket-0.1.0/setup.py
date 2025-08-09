from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dailyutils-aniket",
    version="0.1.0",
    author="Your Name",
    author_email="aniketpatidar70@gmail.com",
    description="A general-purpose daily utility toolkit for everyone: reminders, converters, expenses, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aniket-patidar01/dailyutils",  # Update this to your GitHub link if uploading
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)

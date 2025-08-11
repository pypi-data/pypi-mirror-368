from setuptools import setup, find_packages

setup(
    name="selenium-web-automation-utils",
    version="0.2.2",
    description="A lightweight Selenium automation utility package.",
    author="Kanad Rishiraj (@RoamingSaint)",
    author_email="roamingsaint27@gmail.com",
    url="https://github.com/roamingsaint/selenium-web-automation-utils",
    packages=find_packages(),
    install_requires=[
        "selenium"
    ],
    extras_require={
        "color": ["colorfulPyPrint"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

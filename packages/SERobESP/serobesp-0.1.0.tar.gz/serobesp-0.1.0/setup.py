from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="SERobESP",
    version="0.1.0",
    author="Sarkis Tamaryan",
    author_email="your_email@example.com",  # Замени на свой
    description="Control ESP32-based robot kits via serial or Wi-Fi using a custom shield",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/S001T/SERobESP.git",  # Замени на свой
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Пример: "pyserial>=3.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

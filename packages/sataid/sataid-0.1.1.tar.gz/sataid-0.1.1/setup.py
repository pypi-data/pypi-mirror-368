from setuptools import setup, find_packages

setup(
    name="sataid",
    version="0.1.1",
    author="sepriando",
    author_email="meteo.go@gmail.com",
    description="Pembacaan data SAT-AID dalam format kabur",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
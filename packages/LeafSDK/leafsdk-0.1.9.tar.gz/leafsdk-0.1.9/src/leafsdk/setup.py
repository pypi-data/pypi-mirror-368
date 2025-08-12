from setuptools import setup, find_packages

setup(
    name="leafsdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "leaf-pymavlink",
        "opencv-python",
        "numpy",
        "scipy",
        "rich",
    ],
    entry_points={
        'console_scripts': [
            'leafcli=leafsdk.cli.leafcli:main',
        ],
    },
)
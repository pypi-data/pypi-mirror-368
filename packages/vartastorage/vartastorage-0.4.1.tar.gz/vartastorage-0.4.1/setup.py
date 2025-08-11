import setuptools

setuptools.setup(
    name="vartastorage",
    version="0.4.1",
    description="VARTA Battery",
    long_description="""
        With this Python module you can read modbus registers
        and xml/cgi api values from various VARTA batteries""",
    url="http://github.com/vip0r/vartastorage",
    author="edAndy",
    author_email="an-dy@gmx.de",
    license="APACHE",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    zip_safe=False,
    python_requires=">=3.11",
    install_requires=[
        "pymodbus>=3.11.0",
        "requests",
    ],
)

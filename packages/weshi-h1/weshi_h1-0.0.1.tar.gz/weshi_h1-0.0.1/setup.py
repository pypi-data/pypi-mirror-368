from setuptools import setup, find_packages

setup(
    name="weshi_h1",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'weshi-calc=weshi_h1.main:run_calc'
        ]
    },
    author="Your Name",
    author_email="your@email.com",
    description="Opens Windows Calculator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/slvignesh05/weshi_h1",
    license="MIT",
)

import setuptools
from distutils.core import setup


def setup_package():
    with open("README.md", "r") as f:
        readme = f.read()

    setup(
        name="st-modal",
        install_requires=['streamlit', 'deprecation'],
        version="0.1.2",
        author="Peter van Lunteren",
        author_email="",
        url="https://github.com/teamtv/streamlit_modal",
        packages=setuptools.find_packages(),
        license="BSD",
        description="Modal for streamlit",
        long_description=readme,
        long_description_content_type="text/markdown",
        classifiers=[
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved",
            "Topic :: Scientific/Engineering",
        ]
    )


if __name__ == "__main__":
    setup_package()
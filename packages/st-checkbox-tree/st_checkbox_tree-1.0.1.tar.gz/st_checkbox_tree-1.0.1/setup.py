import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="st-checkbox-tree",
    version="1.0.0",
    author="peteraddax",
    author_email="",
    description="Enhanced Streamlit checkbox tree component with visual tree lines, HTML labels, and extensive customization options",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.6",
    install_requires=[
        "streamlit >= 0.63",
    ],
    keywords="streamlit, checkbox, tree, hierarchical, component, tree-lines, visual-hierarchy",
)


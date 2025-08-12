from setuptools import setup, find_packages  # 🔥 Import find_packages()

setup(
    name="heraldopy",
    version="1.0.16",  # Update version when making changes
    author="Heraldo Almeida",
    author_email="heraldo.almeida@gmail.com",
    description="A set of automation tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/heraldopy",
    packages=find_packages(),  # 🔥 This will now work correctly
    install_requires=[
        "requests",
        "msal",
        "wget",
        "numpy",
        "pandas",
        "tk",
        "rapidfuzz",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

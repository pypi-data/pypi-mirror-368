from setuptools import find_packages, setup

setup(
    name="qlib-py",
    version="1.0.0",
    author="Eric Santos",
    author_email="ericshantos13@gmail.com",
    description="Python reinforcement learning library implementing "
    "Q-learning with raining workflows for object search tasks in grid worlds.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ericshantos/qlib",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy>=2.3.2",
    ],
    extras_require={
        "dev": ["pre-commit>=3.0.0"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

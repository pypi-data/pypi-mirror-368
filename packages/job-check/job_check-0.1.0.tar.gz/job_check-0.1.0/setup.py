from setuptools import setup, find_packages

setup(
    name="job-check",
    version="0.1.0",
    description="A package for job checking and proxy management.",
    author="Jeremy Lo",
    author_email="germanyno062@gmail.com",
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'job-check=jobspy.cli:main',
        ],
    },
    include_package_data=True,
    url="https://github.com/VorpalElf/JobSpy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

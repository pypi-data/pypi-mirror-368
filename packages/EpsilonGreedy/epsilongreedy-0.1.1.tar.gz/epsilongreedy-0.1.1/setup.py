import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EpsilonGreedy",
    version="0.1.1",
    author="Priyanshi Furiya",
    author_email="furiyapriyanshi@gmail.com",
    description="A simple Epsilon-Greedy multi-armed bandit implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Replace with your project's URL
    url="https://github.com/priyanshi-furiya/epsilon-greedy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'epsilon-greedy-sim=EpsilonGreedy.main:main',
        ],
    },
)

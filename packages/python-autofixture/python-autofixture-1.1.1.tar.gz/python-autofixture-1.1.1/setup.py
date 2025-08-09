from setuptools import setup, find_packages

DESCRIPTION = 'A Version of C#s AutoFixture but for python'
LONG_DESCRIPTION = 'Allows creating of fake test data that autogenerates both primitive and deep object graph types'

# Setting up
setup(
    name="python-autofixture",
    version="1.1.1",
    author="GanTheMan",
    author_email="aidanwilliamgannon@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'autofixture', 'python autofixture', 'python testing', 'python autofixture c#'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix"
    ]
)
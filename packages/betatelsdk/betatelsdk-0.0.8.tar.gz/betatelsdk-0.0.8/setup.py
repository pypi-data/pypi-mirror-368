from setuptools import setup, find_packages
import os

VERSION = '0.0.8'
DESCRIPTION = 'An SDK for Betatel services'

# Read the README file for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="betatelsdk",
    version=VERSION,
    author="Betatel LTD",
    author_email="<muhamed.b@beta.tel>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["requests"],
    keywords=['python', 'tts', 'tele', 'voice', 'sms', 'sip', 'call', 'betatel'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
from setuptools import setup, find_packages

with open("README.txt", encoding="utf-8") as f:
    readme = f.read()

with open("changelog.txt", encoding="utf-8") as f:
    changelog = f.read()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='basicgame',
    version='0.0.1',
    description='A simple guessing game in Python',
    long_description=readme + '\n\n' + changelog,
    long_description_content_type="text/plain",
    author='kriti',
    author_email='kritibisht42@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='game',
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6"
)

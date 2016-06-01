from setuptools import setup


# Read the long description from README.rst
with open('README.rst') as f:
    long_description = f.read()


setup(
    name='multi-ssh',
    version='0.1',
    url='https://github.com/fgimian/multi-ssh',
    license='MIT',
    author='Fotis Gimian',
    author_email='fgimiansoftware@gmail.com',
    description=(
        'Execution of commands and the tailing of logs in parallel across '
        'multiple servers'
    ),
    long_description=long_description,
    platforms='Posix',
    py_modules=['multissh'],
    install_requires=[
        'paramiko>=1.10.1',
    ],
)

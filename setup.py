from setuptools import setup

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
    platforms='Posix',
    py_modules=['multissh'],
    install_requires=[
        'paramiko>=1.10.1',
    ],
)

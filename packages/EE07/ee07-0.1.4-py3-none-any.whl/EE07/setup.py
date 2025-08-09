from setuptools import setup, find_packages

setup(
    name='ee07',
    version='0.1.0',
    description='EE07: Double-E Language for Chemical System Programming',
    author='Prakritee Chakraborty',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': ['eel=eel.interpreter:run_code']
    },
    python_requires='>=3.7',
)

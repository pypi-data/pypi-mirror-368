from setuptools import setup, find_packages

def parse_requirements(filename):
    requirements = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            # Skip comments, blank lines, and pip options
            if line and not line.startswith('#') and not line.startswith('-'):
                requirements.append(line)
    return requirements

setup(
    name='aird',
    version='0.2.0',
    packages=find_packages(),
    package_data={'aird': ['templates/*.html']},
    entry_points={
        'console_scripts': [
            'aird=aird.main:main',
        ],
    },
    install_requires=parse_requirements('requirements.txt'),
    author='Viswantha Srinivas P',
    author_email='psviswanatha@gmail.com',  # Please fill this in
    description='Aird - A lightweight web-based file browser and streamer',
    url='https://github.com/blinkerbit/aird',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='Custom',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
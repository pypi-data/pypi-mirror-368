from setuptools import setup, find_packages

setup(
    name="niklibrary",
    version="0.45",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.sh', '*.yml'],
        'NikGapps.helper': ['assets/*'],
        'NikGapps.helper.assets': ['*'],
    },
    author="Nikhil Menghani",
    author_email="nikhil@menghani.com",
    description="A short description of your project",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/nikhilmenghani/niklibrary",
    install_requires=[
        'colorama~=0.4.6',
        'pytz~=2025.2',
        'setuptools~=80.9.0',
        'nikassets~=0.13',
        'GitPython~=3.1.44',
        'PyGithub~=2.6.1',
        'python-gitlab~=6.1.0',
        'beautifulsoup4==4.13.4',
        'requests~=2.32.4',
        'python-dotenv~=1.1.1',
        'pexpect~=4.9.0',
        'psutil~=7.0.0',
        'cryptography~=45.0.5',
        'paramiko~=4.0.0'
    ],
    entry_points={
        'console_scripts': [
            'niklibrary=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.12',
)
from setuptools import setup, find_packages

setup(
    name='junbedded',
    version='0.0.1',
    description='Python Embedded Personal Tools',
    author='wnsdlf925',
    author_email='wnsdlf925@naver.com',
    url='https://github.com/wnsdlf925/junbedded.git',
    install_requires=[],
    packages=find_packages(exclude=[]),
    keywords=['junbedded', 'wnsdlf925', 'python', 'rasberry pi'],
    python_requires='>=3.9',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
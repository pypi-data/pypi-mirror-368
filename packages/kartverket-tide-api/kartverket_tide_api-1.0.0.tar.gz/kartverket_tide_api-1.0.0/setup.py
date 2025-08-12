from setuptools import setup, find_packages

setup(
    name='kartverket_tide_api',
    version='1.0.0',
    license='MIT',
    description='Unofficial library for the Kartverket tide API',
    author='Mats Johan Pedersen',
    author_email='matspedersen@protonmail.com',
    url='https://github.com/matsjp/kartverket_tide_api',
    download_url='https://github.com/matsjp/kartverket_tide_api/archive/refs/tags/v1.0.0.tar.gz',
    keywords=['kartverket', 'tide', 'api'],
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'requests',
        'vcrpy',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
)

from setuptools import setup, find_packages

readme = open('README.md').read()

VERSION = '0.0.8'

requirements = [
]


setup(
    # Metadata
    name='balinski-and-gomory',
    version=VERSION,
    author='cestwc',
    author_email='80936226+cestwc@users.noreply.github.com',
    url='https://github.com/cestwc/primal-linear-assignment',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',

    # Package info
    packages=find_packages(exclude=('*test*',)),

    #
    zip_safe=True,
    install_requires=requirements,

    # Classifiers
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],

    include_package_data=True,
    package_data={
        "balinski_and_gomory.hylac_shortcut": ["libhylac.so"],
        "balinski_and_gomory._cuda": ["solve.cpp", "balinski-and-gomory-cuda/src/*"],
    },
)
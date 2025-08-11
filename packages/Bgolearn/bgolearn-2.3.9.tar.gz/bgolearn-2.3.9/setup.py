from setuptools import setup, find_packages

setup(
    name='Bgolearn',
    version='2.3.9',
    description="A Bayesian global optimization package for material design",
    long_description=open('README.md', encoding='utf-8').read(),
    include_package_data=True,
    author='CaoBin',
    author_email='bcao@shu.edu.com',
    maintainer='CaoBin',
    maintainer_email='binjacobcao@gmail.com',
    license='MIT License',
    url='https://github.com/Bin-Cao/Bgolearn',
    packages=find_packages(),  # Automatically include all Python modules
    package_data={'Bgolearn': ['BgolearnFuns/*']},  # Specify non-Python files to include
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.5',
    install_requires=['scipy', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'multiprocess', 'art'],
    entry_points={
        'console_scripts': [
            '',
        ],
    },
)

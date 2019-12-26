from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
setup(
    name='parliament_members_sankey',
    version='0.3',
    py_modules=['main'],
    # packages=['crawler', 'visualizer', 'configuration', 'pandas_manager'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/drkostas',
    license='',
    author='drkostas',
    author_email='georgiou.kostas94@gmail.com',
    description='Package for creating sankey diagrams for political',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'parliament_members_sankey=main:main'
        ]
    },
)

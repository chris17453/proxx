from setuptools import setup


setup(
    name='proxx',
    version='1.0.0',
    packages=['proxx',],
    include_package_data=True,
    url='https://github.com/chris17453/proxx/',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    summary= 'Proxy configuration for docker,npm,git,yarn and terminal',
    author= 'Charles Watkins',
    author_email= 'charles@titandws.com',
    description= '',
    platform= 'All',    
    install_requires=[
    ],
    #data_files=[
    #    ('share/icons/hicolor/scalable/apps', ['data/proxx.svg']),
    #    ('share/applications', ['data/proxx.desktop'])
    #],
    entry_points="""
        [console_scripts]
        proxx = proxx.cli:main
        """    
    
)




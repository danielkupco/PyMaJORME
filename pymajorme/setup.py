from setuptools import setup

setup(
    name='pymajorme',
    version='0.2.2',
    include_package_data=True,
    py_modules=['pymajorme', 
                'pymajorme_config',
    ],
    packages=['helpers',
              'generators',
              'languages',
              'templates'
    ],
    package_dir={
              'languages' : 'languages',
              'templates' : 'templates'
    },
    package_data={
              'languages' : ['*.tx'],
              'templates' : ['*.template']
    },
    install_requires=[
        'Click==6.2',
        'Arpeggio==1.2.1',
        'decorator==4.0.4',
        'ipython==4.0.1',
        'ipython-genutils==0.1.0',
        'Jinja2==2.8',
        'MarkupSafe==0.23',
        'path.py==8.1.2',
        'pexpect==4.0.1',
        'pickleshare==0.5',
        'ptyprocess==0.5',
        'pydot3k==1.0.17',
        'pyparsing==2.0.6',
        'simplegeneric==0.8.1',
        'textX==0.4.2',
        'traitlets==4.0.0',
        'wheel==0.24.0',
    ],
    entry_points='''
        [console_scripts]
        pymajorme=pymajorme:cli
    ''',
)

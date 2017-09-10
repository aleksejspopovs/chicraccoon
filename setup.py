from setuptools import setup

setup(
    name='chicraccoon',

    version='0.1.0',

    description='A utility for managing backup files from Sharp electronic notebooks',

    url='https://github.com/popoffka/chicraccoon',

    author='Aleksejs Popovs',
    author_email='aleksejs@popovs.lv',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        'Topic :: Office/Business :: News/Diary,'
        'Topic :: Office/Business :: Scheduling',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],

    keywords='sharp enote backup schedule notebook',

    packages=['chicraccoon'],

    install_requires=['Pillow', 'Jinja2'],

    package_data={
        'chicraccoon': ['web_templates/*'],
    },

    entry_points={
        'console_scripts': [
            'chicraccoon_cli=chicraccoon.cli:main',
            'chicraccoon_sync=chicraccoon.sync:main',
        ],
    },
)

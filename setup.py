from setuptools import setup

setup(
        name='trektings',
        packages=['trektings'],
        include_package_data=True,
        install_requires=['flask','sqlalchemy','mariadb']
        )

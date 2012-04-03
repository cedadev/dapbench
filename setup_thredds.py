try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='thredds_security_test',
    version="0.1.3",
    description='THREDDS Data Server security configuration test utilities',
    author='Richard Wilkinson',
    long_description=open('README').read(),
    license='BSD - See LICENCE file for details',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'thredds_test_catalog_access = thredds_security_test.scripts.check_catalog:main',
            'thredds_test_file_access = thredds_security_test.scripts.check_files:main',
            'thredds_test_metadata = thredds_security_test.scripts.check_metadata:main',
            'thredds_test_url_access = thredds_security_test.scripts.check_url:main'
            ]
        }
)

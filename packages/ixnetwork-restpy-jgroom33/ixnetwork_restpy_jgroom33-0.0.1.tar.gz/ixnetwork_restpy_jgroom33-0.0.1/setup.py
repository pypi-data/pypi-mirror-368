import os
import sys
import time
from setuptools import setup, find_packages


base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, 'README.md')) as fid:
    long_description = fid.read()

if '-sdk_version' in sys.argv:
    version_number = sys.argv[-1]
    sys.argv.pop()
    sys.argv.remove('-sdk_version')
elif '--internal' in sys.argv:
    version_number = time.strftime('%Y%m%d.%H.%M', time.gmtime())
    sys.argv.remove('--internal')
else:
    with open(os.path.join(base_dir, 'version.txt')) as fid:
        version_number = fid.read()


setup(
    name='ixnetwork_restpy-jgroom33',
    version=version_number,
    description='The IxNetwork Python Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jgroom33/ixnetwork_restpy',
    author='Ciena Corporation',
    author_email='jgroom@ciena.com',
    license='MIT',
    license_files=('LICENSE', ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='ixnetwork performance traffic generator real world ixia automation',
    packages=find_packages(
        include=['ixnetwork_restpy*'],
        exclude=['ixnetwork_restpy.tests*', 'tests*', 'samples*', 'docs*', 'pytest_tests*']
    ),
    include_package_data=True,
    python_requires='>=2.7, <4',
    install_requires=['requests', 'websocket-client', 'packaging'],
    tests_require=['mock'],
    test_suite='ixnetwork_restpy.tests'
)

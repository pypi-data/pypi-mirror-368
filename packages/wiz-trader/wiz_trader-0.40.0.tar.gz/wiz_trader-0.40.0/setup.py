from setuptools import setup, find_packages

setup(
  name='wiz_trader',
  version='0.39.0',
  description='A Python SDK for connecting to the Wizzer.',
  long_description=open('README.md').read() if open('README.md') else "",
  long_description_content_type='text/markdown',
  author='Pawan Wagh',
  author_email='pawan@wizzer.in',
  url='https://bitbucket.org/wizzer-tech/quotes_sdk.git',
  packages=find_packages(),
  install_requires=[
    'websockets',
    'requests',
    'python-dotenv'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Financial and Insurance Industry',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Topic :: Office/Business :: Financial',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  python_requires='>=3.6',
  include_package_data=True,
)

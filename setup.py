from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='tptp_tools',
      version='0.1',
      description='A library for handling TPTP related input and systems',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Parser :: Editor module',
      ],
      keywords='parse and request on TPTP.org',
      url='https://git.imp.fu-berlin.de/josince89/logik-softwareprojekt',
      author='León Dirmeier',
      author_email='leon.dirmeier@fu-berlin.de',
      license='MIT',
      packages=['tptp_tools'],
      install_requires=[
          'lxml',
          'requests',
	  'antlr4-python3-runtime==4.7.1',
	  'pyperclip==1.7.0'

      ],
      include_package_data=True,
      zip_safe=False)

from setuptools import setup

setup(name='aidapy',
      version='0.0.1',
      description='AIDA Python Toolkit',
      url='http://gitlab.cern.ch/ddavis/aidapy',
      author='Doug Davis',
      author_email='ddavis@cern.ch',
      license='MIT',
      install_requires=[
          'numpy',
      ],
      packages=['aidapy',
                'aidapy.hist',
                'aidapy.meta',
                'aidapy.plot'
      ]
)

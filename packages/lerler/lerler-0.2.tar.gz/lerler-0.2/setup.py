from setuptools import setup, find_packages

setup(name='lerler',
      version='0.2',
      packages=find_packages(),
      install_requires=[
          'numpy >= 1.0.0',
      ],
      entry_points={
          'console_scripts': [
              'lerler = lerler.main:hello'
          ]
      })
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(name='lerler',
      version='0.3',
      packages=find_packages(),
      install_requires=[
          'numpy >= 1.0.0',
      ],
      entry_points={
          'console_scripts': [
              'lerler = lerler.main:hello'
          ]
      },
      long_description=description,
      long_description_content_type="text/markdown")
from setuptools import setup

with open("README.rst", encoding='utf-8') as f:
    long_description = f.read()

setup(name='FreeWork',  # 包名
      version='1.0.5',  # 版本号
      description='简单又实用的office操作函数！(Simple and practical office operation functions!)',
      long_description=long_description,
      author='Jhonie King(王骏诚)',
      author_email='queenelsaofarendelle2022@gmail.com',
      license='MIT License',
      packages=["FreeWork"],
      keywords=['python', 'Office', 'Excle', 'Word', 'File\'s operation'],
      install_requires=['openpyxl', 'python-docx', 'pytest-shutil', 'fiona', 'pandas', 'geopandas', 'spire.doc.free'],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )

from setuptools import setup, find_packages

setup(name='pylog',
      version='0.0.0',
      description='A debugger that logs program execution and lets you play with the results',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2.6',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
      ],
      url='https://github.com/mattboehm/pylog',
      author='Matthew Boehm',
      author_email='boehm.matthew@gmail.com',
      license='MPL 2.0',
      packages=find_packages(),
      package_data={
          "": ["static/*"],
      },
      include_package_data=True,
      install_requires=[
        'bottle',
        'docopt',
        'six',
      ],
      entry_points={
        'console_scripts': ['pylog=pylog.cli:main', 'pylog-web=pylog.webviewer:main'],
      },
      zip_safe=False)

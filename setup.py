from setuptools import setup, find_packages
import sys


setup(name='renv_device',
      version='0.0.2',
      url = 'http://ogata-lab.jp/',
      author = 'ysuga',
      author_email = 'ysuga@ysuga.net',
      description = 'Renv Device Programming library',
      download_url = 'https://github.com/ogata-lab/python_renv_device',
      packages = ["renv_device"],
      #py_modules = ["pepper_kinematics"],
      license = 'GPLv3',
      install_requires = ['websocket-client', 'bitstring', 'pyyaml'],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        ],
      #test_suite = "foo_test.suite",
      #package_dir = {'': 'src'}
    )

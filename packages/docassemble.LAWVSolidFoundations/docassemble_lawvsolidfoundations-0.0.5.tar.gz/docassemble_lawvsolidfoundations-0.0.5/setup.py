import os
import sys
from setuptools import setup, find_namespace_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.LAWVSolidFoundations',
      version='0.0.5',
      description=('A docassemble extension.'),
      long_description='LAWV Solid Foundations is a project supported by the Pro Bono unit at Legal Aid of West Virginia aimed at providing clients in need a guardianship or adoption with some pleadings and paperwork for court and their estate. The interview is intended to be conducted in a clinic-like setting working with an attorney rather than a fully self-guided process.  The code is an amalgamation of the LAWV Kinship Connector and the LAWV Will Clinic interviews.',
      long_description_content_type='text/markdown',
      author='System Administrator',
      author_email='dhenry@lawv.net',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_namespace_packages(),
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/LAWVSolidFoundations/', package='docassemble.LAWVSolidFoundations'),
     )


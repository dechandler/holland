from setuptools import setup, find_packages
import sys, os

version = '0.9.9'

setup(name='holland.backup.pgdump',
      version=version,
      description="Holland pg_dump backup plugin",
      long_description="""\
      Postgres pg_dump backup""",
      author='Rackspace',
      author_email='support@rackspace.com',
      url='https://gforge.rackspace.com/gf/project/holland',
      license='GPLv2',
      packages=['holland'],
      namespace_packages=['holland', 'holland.backup'],
      zip_safe=True,
      # holland looks for plugins in holland.backup
      entry_points="""
      [holland.backup]
      pgdump = holland.backup.pgdump:Pgdump
      """
)
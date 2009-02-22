from setuptools import setup, find_packages

version = '0.1'

setup(name='afpy.barcamp',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['afpy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools>=0.6c9',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        # Add extra requirements here
                        'z3c.flashmessage >= 1.0',
                        'zope.sendmail',
                        'megrok.menu',
                        'zc.sourcefactory',
                        ],
      entry_points="""
      # Add entry points here
      [paste.app_factory]
      main = afpy.barcamp.startup:application_factory
      """,
      )

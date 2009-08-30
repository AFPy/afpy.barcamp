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
      author="Christophe Combelles",
      author_email="ccomb@free.fr",
      url="https://hg.afpy.org/afpy.barcamp/",
      license="GPL v2",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['afpy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['distribute',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        # Add extra requirements here
                        'z3c.flashmessage >= 1.0',
                        'zope.sendmail',
                        'megrok.menu',
                        'zc.sourcefactory',
                        'xlwt'
                        ],
      entry_points="""
      # Add entry points here
      [paste.app_factory]
      main = afpy.barcamp.startup:application_factory
      """,
      )

afpy.barcamp
============

Barcamp and other conference-like web application.

TODO: add here a high level overview of the project


Set up the dev environment
--------------------------

Clone the source code with ``mercurial``::

  $ hg clone https://hg.afpy.org/afpy.barcamp

Install ``virtualenv`` and set the ``afpy.barcamp`` folder as the root
of the environment::

  $ sudo easy_install virtualenv
  $ virtualenv --no-site-package ./afpy.barcamp
  $ cd afpy.barcamp
  $ source bin/activate

The goal of ``virtualenv`` is to isolate the python dependencies of the
``afpy.barcamp`` project to make it completely independent of the system
python libs.

You can then configure your ``~/.buildout/default.cfg`` to configure
and eggs cache folder such as::

  [buildout]
  eggs-directory = /home/joeuser/.buildout/eggs

Launch the bootstrap script that fetches the buildout utility::

  $ ./bin/python bootstrap.py

Launch the buildout that will install all dependencies (grok, zope
libraries, ...) and setup an inplace grok/zope instance::

  $ ./bin/buildout

Have a coffee.

Then you can start the default zserver on the default port::

  $ ./bin/zopectl fg

You can alternatively launch a paste server using::

  $ ./bin/paster server debug.ini

Using paste makes it possible to use an ``afpy.barcamp`` instance as a WSGI
application.

In both cases the application is available at http://localhost:8080/ .


Launching the tests
===================

Use the default zope testrunner::

  $ ./bin/test


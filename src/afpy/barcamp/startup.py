# -*- coding: utf-8 -*-
import os
import sys
import code
import zdaemon.zdctl
import zope.app.wsgi
import zope.app.debug

def application_factory(global_conf, conf):
    zope_conf = os.path.join(global_conf['here'], conf)
    return zope.app.wsgi.getWSGIApplication(zope_conf)




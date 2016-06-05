# -*- coding: utf-8 -*-
__author__ = 'Alexandr'

import webapp2
from views import GroupSelectionPage, DoTheMagic, ItsAlive, decorator

application = webapp2.WSGIApplication([
    ('/', GroupSelectionPage),
    ('/dothemagic', DoTheMagic),
    ('/its-alive', ItsAlive),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)

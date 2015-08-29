# -*- coding: utf-8 -*-
__author__ = 'alexandr'

import os
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

BASE_URL = "http://rasp.nsuem.ru/"


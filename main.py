#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import os
import sys
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images


from impl import activities
from impl import photos
from impl import planners


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({
            "loginurl": users.create_login_url('/account/')
        }))

class AccountHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template('home.html')
            self.response.write(template.render({
                'name': user.nickname(), 
                "logouturl": users.create_logout_url('/')
            }))
        else:
            self.redirect('/')



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/account/.*', AccountHandler),
    ('/services/planners/', planners.PlannersServiceHandler),
    ('/services/planners/([^/]+)', planners.PlannerServiceHandler),
    ('/services/photos/', photos.PhotoServiceHandler),
    ('/services/photos/([^/]+)', photos.PhotoServiceHandler),
    ('/services/photo/([^/]+)', photos.SinglePhotoServiceHandler),
    ('/services/planners/([^/]+)/activities/', activities.PlannerActivityServiceHandler),
    ('/services/activities/([^/]+)', activities.ActivityServiceHandler),
    ('/services/dayactivities/([^/]+)/([^/]+)', activities.ActivityDayServiceHandler)
], debug=True)




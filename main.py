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

class PlannerEntry(ndb.Model):
    name = ndb.StringProperty(required=True)
    creator = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class PhotoEntry(ndb.Model):
    name = ndb.StringProperty(required=True)
    creator = ndb.StringProperty(required=True)
    contenttype = ndb.StringProperty(required=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.BlobProperty(indexed=False)



def getPhotos(user):
    # ndb.delete_multi(
    #     PlannerEntry.query().fetch(keys_only=True)
    # )

    query = PhotoEntry.query(PhotoEntry.creator == user.user_id()).order(PhotoEntry.name)
    entries = query.fetch(100, projection=[PhotoEntry.name, PhotoEntry.contenttype, PhotoEntry.date])

    photos = []
    for p in entries:
        photos.append({
            "key": p.key.urlsafe(),
            "name": p.name,
            "contenttype": p.contenttype,
            "creationdate": str(p.date)
        });
    return photos

def getPhoto(user, id):
    p = ndb.Key(urlsafe=id).get()
    if p and p.creator != user.user_id():
        return None
    return p

def hasPhotos(user):
    query = PhotoEntry.query(PhotoEntry.creator == user.user_id())
    return query.count(keys_only=True) > 0


def getPlanners(user):
    planner_query = PlannerEntry.query(PlannerEntry.creator == user.user_id()).order(PlannerEntry.name)
    planner_entries = planner_query.fetch(10)

    schedules = []
    for p in planner_entries:
        schedules.append({
            "key": p.key.urlsafe(),
            "name": p.name,
            "creator": p.creator,
            "description": p.description,
            "creationdate": str(p.date)
        });
    return schedules

def hasPlanners(user):
    query = PlannerEntry.query(PlannerEntry.creator == user.user_id())
    return query.count(keys_only=True) > 0


def isPlannerExist(user, name):
    planner_query = PlannerEntry.query(PlannerEntry.creator == user.user_id() and PlannerEntry.name == name).order(PlannerEntry.name)
    planner_entries = planner_query.fetch(1)

    return len(planner_entries) > 0;


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
                "logouturl": users.create_logout_url('/'),
                "hasPlanners" : hasPlanners(user),
                "hasPhotos" : hasPhotos(user)
            }))
        else:
            self.redirect('/')


class PlannerServiceHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()

        try:
            data = json.loads(self.request.body)

            if 'description' not in data:
                data['description'] = ''
            data['description'] = data['description'].strip()

            if ('name' not in data or data['name'].strip() == '') :
                self.response.write("name is missing")
                self.response.set_status(400)
            elif isPlannerExist(user, data['name'].strip()):
                self.response.write("name already exist")
                self.response.set_status(400)
            else:
                greeting = PlannerEntry()
                greeting.name = data['name'].strip()
                greeting.description = data['description'].strip()
                greeting.creator = user.user_id()
                greeting.put();
        except ValueError:
            self.response.write('payload is not correct')
            self.response.set_status(400)
        except:
            e = sys.exc_info()[0]
            self.response.write("%s" % e)
            self.response.set_status(400)

    def get(self):
        user = users.get_current_user()
        planners = getPlanners(user)
        self.response.write(json.dumps(planners))

    def delete(self, id):
        user = users.get_current_user()
        entry = ndb.Key(urlsafe=id).get()
        if entry is None:
            self.response.write('not found')
            self.response.set_status(400)
        elif entry.creator == user.user_id():
            ndb.Key(urlsafe=id).delete()
        else:
            self.response.write('not found')
            self.response.set_status(400)


class PhotoServiceHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        file = self.request.POST["file_data"] 
        error = None

        if file is not None:
            tyep = file.type
            if tyep == 'image/png' or tyep == 'image/jpeg' or tyep == 'image/jpg':
                photo = PhotoEntry()
                photo.name = file.filename.strip()
                photo.creator = user.user_id()
                photo.contenttype = tyep
                photo.data = file.file.read()
                photo.put();
                self.response.write("{}")
            else:
                error = 'Unsupported file type'
        else:
            error = 'Empty Content'

        if error is not None:
            self.response.write(error)
            self.response.set_status(400)        

    def get(self):
        photos = getPhotos(users.get_current_user())
        self.response.write(json.dumps(photos))

class SinglePhotoServiceHandler(webapp2.RequestHandler):
    def get(self, id):
        photo = getPhoto(users.get_current_user(), id)
        if photo:
            self.response.headers['Content-Type'] = str(photo.contenttype)
            self.response.out.write(photo.data)
        else:
            self.response.write('not found')
            self.response.set_status(400)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/account/.*', AccountHandler),
    ('/services/planners/', PlannerServiceHandler),
    ('/services/planners/([^/]+)', PlannerServiceHandler),
    ('/services/photos/', PhotoServiceHandler),
    ('/services/photo/([^/]+)', SinglePhotoServiceHandler)
], debug=True)




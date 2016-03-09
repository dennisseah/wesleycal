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


def to24Hours(t):
    test = t.split(' ')
    if test[1] == 'PM':
        test = test[0].split(':')
        return str(int(test[0]) + 12) + test[1];
    else:
        test = test[0].split(':')
        return test[0] + test[1];

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


class ActivityEntry(ndb.Model):
    planner = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    creator = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=True)
    startdate = ndb.IntegerProperty(required=True)
    starttime = ndb.IntegerProperty(required=False)
    duration = ndb.IntegerProperty(required=False)
    day0 = ndb.BooleanProperty(required=False)
    day1 = ndb.BooleanProperty(required=False)
    day2 = ndb.BooleanProperty(required=False)
    day3 = ndb.BooleanProperty(required=False)
    day4 = ndb.BooleanProperty(required=False)
    day5 = ndb.BooleanProperty(required=False)
    day6 = ndb.BooleanProperty(required=False)

def to12Hours(t):
    ampm = 'AM'
    if t >= 1300:
        t = t - 1200
        ampm= 'PM'
    elif t >= 1200:
        ampm= 'PM'

    s = str(t);
    if len(s) == 4:
        return s[0:2] + ':' + s[2:] + ' ' + ampm;
    return s[0:1] + ':' + s[1:] + ' ' + ampm;


def getActivities(user, planner):
    query = ActivityEntry.query(ActivityEntry.creator == user.user_id() and ActivityEntry.planner == planner).order(ActivityEntry.starttime)
    entries = query.fetch(1000)

    activities = []
    for a in entries:
        activities.append({
            "key": a.key.urlsafe(),
            "name": a.name,
            "description": a.description,
            "creator": a.creator,
            "planner": a.planner,
            "picture": a.picture,
            "startdate": str(a.startdate),
            "starttime": to12Hours(a.starttime),
            "duration": str(a.duration),
            "day0": a.day0,
            "day1": a.day1,
            "day2": a.day2,
            "day3": a.day3,
            "day4": a.day4,
            "day5": a.day5,
            "day6": a.day6
        });
    return activities


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
                "logouturl": users.create_logout_url('/')
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

class SinglePhotoServiceHandler(webapp2.RequestHandler):
    def get(self, id):
        photo = getPhoto(users.get_current_user(), id)
        if photo:
            self.response.headers['Content-Type'] = str(photo.contenttype)
            self.response.out.write(photo.data)
        else:
            self.response.write('not found')
            self.response.set_status(400)


class ActivityServiceHandler(webapp2.RequestHandler):
    def post(self, planner):
        user = users.get_current_user()

        try:
            data = json.loads(self.request.body)

            if 'description' not in data:
                data['description'] = ''
            data['description'] = data['description'].strip()

            if ('name' not in data or data['name'].strip() == '') :
                self.response.write("name is missing")
                self.response.set_status(400)
            if ('picture' not in data or data['picture'].strip() == '') :
                self.response.write("picture is missing")
                self.response.set_status(400)
            if ('starttime' not in data or data['starttime'].strip() == '') :
                self.response.write("starttime is missing")
                self.response.set_status(400)
            elif ('duration' not in data or data['duration'].strip() == '' or not data['duration'].isnumeric()) :
                self.response.write("duration is missing or is non numeric")
                self.response.set_status(400)
            else:
                activity = ActivityEntry()
                activity.planner = planner
                activity.name = data['name'].strip()
                activity.description = data['description'].strip()
                activity.picture = data['picture'].strip()
                activity.creator = user.user_id()
                activity.duration = int(data['duration'])
                activity.startdate = 0 if ('startdate' not in data or data['startdate'].strip() == '') else int(data['startdate'])
                activity.starttime = int(to24Hours(data['starttime']))
                activity.day0 = data['day0']
                activity.day1 = data['day1']
                activity.day2 = data['day2']
                activity.day3 = data['day3']
                activity.day4 = data['day4']
                activity.day5 = data['day5']
                activity.day6 = data['day6']
                activity.put();
        except ValueError:
            self.response.write('payload is not correct')
            self.response.set_status(400)
        except:
            e = sys.exc_info()[0]
            self.response.write("%s" % e)
            self.response.set_status(400)

    def get(self, planner):
        activities = getActivities(users.get_current_user(), planner)
        self.response.write(json.dumps(activities))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/account/.*', AccountHandler),
    ('/services/planners/', PlannerServiceHandler),
    ('/services/planners/([^/]+)', PlannerServiceHandler),
    ('/services/photos/', PhotoServiceHandler),
    ('/services/photos/([^/]+)', PhotoServiceHandler),
    ('/services/photo/([^/]+)', SinglePhotoServiceHandler),
    ('/services/activities/([^/]+)', ActivityServiceHandler)
], debug=True)




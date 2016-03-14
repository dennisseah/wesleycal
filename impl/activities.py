import json
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

from impl import common
from datetime import date


class ActivityEntry(ndb.Model):
    planner = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    creator = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=True)
    startdate = ndb.IntegerProperty(required=True)
    enddate = ndb.IntegerProperty(required=True)
    starttime = ndb.IntegerProperty(required=False)
    duration = ndb.IntegerProperty(required=False)
    day0 = ndb.BooleanProperty(required=False)
    day1 = ndb.BooleanProperty(required=False)
    day2 = ndb.BooleanProperty(required=False)
    day3 = ndb.BooleanProperty(required=False)
    day4 = ndb.BooleanProperty(required=False)
    day5 = ndb.BooleanProperty(required=False)
    day6 = ndb.BooleanProperty(required=False)

def getActivities(user, planner):
    query = ActivityEntry.query(ActivityEntry.creator == user.user_id() and \
        ActivityEntry.planner == planner).order(ActivityEntry.starttime)
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
            "enddate": str(a.enddate),
            "starttime": common.to12Hours(a.starttime),
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


def getDayActivities(user, planner, day, d):
    query = ActivityEntry.query()
    query = query.filter( \
        ndb.GenericProperty('creator') == user.user_id()).filter( \
        ndb.GenericProperty('planner') == planner).filter( \
        ndb.GenericProperty('day' + str(day)) == True)

    query = query.filter(ndb.OR( \
        ndb.GenericProperty('startdate') >= d, \
        ndb.GenericProperty('startdate') == 0 \
    ))

    entries = query.fetch(1000)

    activities = []
    for a in entries:
        if a.enddate == 0 or a.enddate <= d:
            activities.append({
                "key": a.key.urlsafe(),
                "name": a.name,
                "description": a.description,
                "picture": a.picture,
                "starttime": a.starttime,
                "duration": str(a.duration),
            });

    activities.sort(key=lambda x: x['starttime'])
    for a in activities:
        a['starttime'] = common.to12Hours(a['starttime'])

    return activities


def parseDay(day):
    if len(day) != 8:
        raise ValueError('invalid date')
    if not day.isdigit():
        raise ValueError('invalid date')
    return date(int(day[0:4]), int(day[4:6]), int(day[6:]))

def normalizeDayOfWeek(d):
    wday = d.weekday() +1
    return 0 if wday == 7 else wday

class ActivityDayServiceHandler(webapp2.RequestHandler):
    def get(self, planner, day):
        try:
            curdate = parseDay(day)
            currwday = normalizeDayOfWeek(curdate)
            user = users.get_current_user()
            activities = getDayActivities(user, planner, currwday, int(day))
            self.response.write(json.dumps(activities))
        except ValueError as ve:
            self.response.write(ve)
            self.response.set_status(400)


class PlannerActivityServiceHandler(webapp2.RequestHandler):
    def get(self, planner):
        activities = getActivities(users.get_current_user(), planner)
        self.response.write(json.dumps(activities))


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
                activity.enddate = 0 if ('enddate' not in data or data['enddate'].strip() == '') else int(data['enddate'])
                activity.starttime = int(common.to24Hours(data['starttime']))
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


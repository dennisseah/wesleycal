import json
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users


class PlannerEntry(ndb.Model):
    name = ndb.StringProperty(required=True)
    creator = ndb.StringProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)




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

def getPlanner(user, id):
    user = users.get_current_user()
    entry = ndb.Key(urlsafe=id).get()
    if entry is None:
        self.response.write('not found')
        self.response.set_status(400)
    elif entry.creator == user.user_id():
        return {
            "key": id,
            "name": entry.name,
            "creator": entry.creator,
            "description": entry.description,
            "creationdate": str(entry.date)
        }
    else:
        self.response.write('not found')
        self.response.set_status(400)

def hasPlanners(user):
    query = PlannerEntry.query(PlannerEntry.creator == user.user_id())
    return query.count(keys_only=True) > 0


def isPlannerExist(user, name):
    planner_query = PlannerEntry.query(PlannerEntry.creator == user.user_id() \
        and PlannerEntry.name == name).order(PlannerEntry.name)
    planner_entries = planner_query.fetch(1)
    return len(planner_entries) > 0;
    

class PlannerServiceHandler(webapp2.RequestHandler):
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

    def get(self, id):
        user = users.get_current_user()
        planner = getPlanner(user, id)
        self.response.write(json.dumps(planner))            

class PlannersServiceHandler(webapp2.RequestHandler):
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

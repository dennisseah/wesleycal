import json
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users


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


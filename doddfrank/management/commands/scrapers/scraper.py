from pymongo import Connection

class Scraper(object):

    def save_data(self, data):
        data['agency'] = self.agency
        data['hash'] = hash(str(data))
        c = Connection()
        db = c.test
        db.meetings.ensure_index('hash', unique=True)
        obj = db.meetings.insert(data)
        print obj
        return obj

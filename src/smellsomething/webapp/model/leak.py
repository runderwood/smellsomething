from . import Model
from time import time

class LeakModel(Model):

    _tablename = 'leak'
    _modelname = 'Leak'

    def count(self,*args,**kwargs):
        cur = self.db.cursor()
        cur.execute("select count(*) as total_leaks from leak")
        tot_row = cur.fetchone()
        total = False
        if tot_row:
            total = tot_row[0]
        cur.close()
        return total

    def create(self,*args,**kwargs):
        newleak = {}
        newleak['title'] = kwargs.get("title", '')
        newleak['description'] = kwargs.get("description", '')
        newleak['created'] = int(kwargs.get("created", time()))
        newleak['modified'] = int(kwargs.get("modified", time()))
        newleak['flags'] = int(kwargs.get("flags", 0))
        newleak['location'] = kwargs.get("location", None)
        cur = self.db.cursor()
        cur.execute( \
            'insert into leak (title, description, created, modified, flags, location) values '+\
            '(%(title)s,%(description)s,%(created)s,%(modified)s,%(flags)s,ST_GeomFromText(%(location)s, 4326)) returning id',\
            newleak\
        )
        result = cur.fetchone()
        if result:
            result = result[0]
        else:
            result = False
        cur.close()
        return result

    def update(self,*args,**kwargs):
        l = kwargs
        l['modified'] = int(time())
        cur = self.db.cursor()
        sql = 'update leak set title=%(title)s, description=%(description)s, '+ \
            'flags=%(flags)s, location=ST_GeomFromText(%(location)s, 4326), modified=%(modified)s '+\
            'returning id'
        cur.execute(sql, l)
        r = cur.fetchone()
        if r:
            r = True
        else:
            r = False
        return r

    def list(self,**kwargs):
        limit = int(kwargs.get("limit", self.DEF_LIMIT))
        offset = int(kwargs.get("offset", 0))
        cur = self.db.cursor()
        cur.execute("select id, title, description, created, modified, ST_AsText(location), flags from leak limit %s offset %s", (limit,offset))
        cols = ('id', 'title', 'description', 'created', 'modified', 'location', 'flags')
        r = cur.fetchall()
        leaks = [dict(zip(cols,row)) for row in r]
        return leaks

    def read(self,**kwargs):
        lid = kwargs.get("id", False)
        l = False
        if lid:
            cur = self.db.cursor()
            cur.execute('select id, title, description, created, modified, ST_AsText(location), flags from leak where id = %s', (lid,))
            cols = ('id', 'title', 'description', 'created', 'modified', 'location', 'flags')
            r = cur.fetchone()
            if r:
                l = dict(zip(cols,r))
        return l

import inspect
import psycopg2
from bottle import HTTPError

class PSQLPlugin(object):
    ''' This plugin passes an sqlite3 database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. '''

    name = 'psql'
    api = 2

    def __init__(self,dbname=False,autocommit=True,keyword='psql',dbhost='localhost',dbuser=None,dbpass=None,dbport=5432):
        self.dbname = dbname
        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbport = dbport
        self.autocommit = autocommit
        self.keyword = keyword

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
        keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, PSQLPlugin): 
                continue
            if other.keyword == self.keyword:
                raise PluginError("Found another psql plugin with "\
                    "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.
        conf = context.get("config", {}).get('psql') or {}
        dbname = conf.get('dbname', self.dbname)
        dbuser = conf.get('dbuser', self.dbuser)
        dbpass = conf.get('dbpass', self.dbpass)
        dbhost = conf.get('dbhost', self.dbhost)
        dbport = conf.get('dbport', self.dbport)
        autocommit = conf.get('autocommit', self.autocommit)
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(callback)[0]
        if keyword not in args:
            return callback
                                               
        def wrapper(*args, **kwargs):

            # Connect to the database
            db = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (dbhost,dbname,dbuser,dbpass))
            # Add the connection handle as a keyword argument.
            kwargs[keyword] = db

            try:
                rv = context.get("callback")(*args, **kwargs)
                if autocommit: 
                    db.commit()
            except Exception as e:
                db.rollback()
                raise HTTPError(500, "Internal Server Error", e)
            finally:
                db.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

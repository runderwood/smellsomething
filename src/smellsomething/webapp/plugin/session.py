import inspect
import bottle
from beaker.middleware import SessionMiddleware

class SessionPlugin(object):

    name = 'session'
    api = 2

    def __init__(self,sessdir='/tmp/',autosave=True,keyword='session',sesstype='file',cookieexp=360):
        self.sessdir = sessdir
        self.sesstype = sesstype
        self.cookieexp = cookieexp
        self.autosave = autosave
        self.keyword = keyword

    def setup(self,app):
        for other in app.plugins:
            if not isinstance(other, SessionPlugin): 
                continue
            if other.keyword == self.keyword:
                raise PluginError("Found another session plugin with "\
                    "conflicting settings (non-unique keyword).")

    def apply(self,callback,context):
        # Override global configuration with route-specific values.
        conf = context.get("config", {}).get('session') or {}
        autosave = conf.get('autosave', self.autosave)
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'session' keyword.
        # Ignore it if it does not need a session handle.
        args = inspect.getargspec(callback)[0]
        if keyword not in args:
            return callback

        session_opts = {
            'session.type': self.sesstype,
            'session.cookie_expires': self.cookieexp,
            'session.data_dir': self.sessdir,
            'session.auto': self.autosave
        }

        app = context.get("app", None)
        sessapp = SessionMiddleware(app, session_opts)

        def wrapper(*args, **kwargs):
            return str(bottle.request.environ)
            session = bottle.request.environ.get('beaker.session')
            kwargs[keyword] = session
            
            try:
                rv = context.get("callback")(*args, **kwargs)
            except Exception as e:
                raise bottle.HTTPError(500, "Session Error", e)
            finally:
                pass
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper

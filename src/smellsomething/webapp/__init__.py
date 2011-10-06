from bottle import Bottle, request, route, run, mako_view as view, mako_template as template, debug, HTTPError, abort, HTTPResponse, response
from .config import Config, DevConfig
import simplejson as json
from .plugin.psql import PSQLPlugin
from beaker.middleware import SessionMiddleware

app = Bottle()
conf = DevConfig()

class StripPathMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)

middleapp = StripPathMiddleware(app)

debug(conf.debug)

session_opts = {
    'session.type': conf.sesstype,
    'session.cookie_expires': conf.sesscookieexp,
    'session.data_dir': conf.sessdir,
    'session.auto': conf.sessautosave
}

psqlplug = PSQLPlugin(dbhost=conf.dbhost,dbname=conf.dbname,dbuser=conf.dbuser,dbpass=conf.dbpass)
app.install(psqlplug)

def svcabort(status=500,error="Internal server error."):
    response.status = status
    return {'error': error}

@app.route('/')
def home():
    t = template('home')
    return t 

@app.get('/services')
def services_discovery():
    return {"services": []}

@app.get('/services/leaks')
def leaks_list(psql):
    max_limit = 1000
    min_limit = 10
    l = max(min_limit, min(max_limit, request.GET.get("l", max_limit)))
    o = int(request.GET.get("o", 0))
    from .model.leak import LeakModel
    lm = LeakModel(db=psql)
    total = lm.count()
    leaks = lm.list(offset=o,limit=l)
    return {"leaks": leaks, "limit": l, "offset": o, "max_limit": max_limit, "min_limit": min_limit, "total": total}

@app.post('/services/leaks')
def add_leak(psql):
    ct = request.headers.get("Content-Type", None)
    if not ct or ct.strip().lower() != "application/json":
        return svcabort(400, "JSON only.")
    try:
        data = json.loads(request.body.read())
    except Exception as e:
        raise HTTPError(400, "Bad data.", e)
    from .model.leak import LeakModel
    newleakid = False
    try:
        newleakid = LeakModel(db=psql).create(**data)
    except Exception as e:
        return svcabort(400, str(e))
    #response.status = 201
    # location header?
    return {"status": "ok", "location": "services/leaks/%d" % (newleakid,)}

@app.get('/services/leaks/:leak_id')
def get_leak(psql,leak_id=None):
    from .model.leak import LeakModel
    lm = LeakModel(db=psql)
    leak = lm.read(id=leak_id)
    if not leak:
        return svcabort(404, 'Not found.')
    return {"status": "ok", "leak": leak}

@app.put('/services/leaks/:leak_id')
def update_leak(psql,leak_id=None):


    ct = request.headers.get("Content-Type", None)
    if not ct or ct.strip().lower() != "application/json":
        return svcabort(400, "JSON only.")
    try:
        data = json.loads(request.body.read())
    except Exception as e:
        raise HTTPError(400, "Bad data.", e)

    from .model.leak import LeakModel
    lm = LeakModel(db=psql)
    leak = lm.read(id=leak_id)
    if not leak:
        return svcabort(404, 'Not found.')

    for k in leak.keys():
        leak[k] = data.get(k, leak[k])

    updated = False
    try:
        updated = lm.update(**leak)
    except Exception as e:
        return svcabort(500, 'Could not update(1).')
    if not updated:
        return svcabort(500, 'Could not update(2).')
    # status...
    return {"status": "ok"}


app = SessionMiddleware(middleapp, session_opts)

from bottle import Bottle, request, route, run, mako_view as view, mako_template as template, debug
from .config import Config, DevConfig
import simplejson as json
from .plugin.psql import PSQLPlugin
from beaker.middleware import SessionMiddleware

app = Bottle()
conf = DevConfig()

debug(conf.debug)

session_opts = {
    'session.type': conf.sesstype,
    'session.cookie_expires': conf.sesscookieexp,
    'session.data_dir': conf.sessdir,
    'session.auto': conf.sessautosave
}

psqlplug = PSQLPlugin(dbhost=conf.dbhost,dbname=conf.dbname,dbuser=conf.dbuser,dbpass=conf.dbpass)
app.install(psqlplug)

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
    cur = psql.cursor()
    cur.execute("select count(*) as total_leaks from leak")
    tot_row = cur.fetchone()
    total = 0
    if tot_row:
        total = tot_row[0]
    cur.execute("select id, title, description, created, modified, ST_AsText(location) from leak limit %s offset %s", (l,o))
    cols = ('id', 'title', 'description', 'created', 'modified', 'location')
    r = cur.fetchall()
    leaks = [dict(zip(cols,row)) for row in r]
    return {"leaks": leaks, "limit": l, "offset": o, "max_limit": max_limit, "min_limit": min_limit, "total": total}

@app.post('/services/leaks')
def add_leak(psql):
    # post json here
    # insert into leak (location) values (ST_GeomFromText('POINT(-126.4 45.32)', 4326))
    return {"status": "ok", "location": "services/leaks/<id>"}


app = SessionMiddleware(app, session_opts)

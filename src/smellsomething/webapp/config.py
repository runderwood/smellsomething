class Config:

    host = 'localhost'
    port = 8787
    debug = False
    auto_reload = False

    dbname = 'smellsomething'
    dbhost = 'localhost'
    dbuser = 'smellsomething'
    dbpass = 'smellsomething'

    sesstype = 'file'
    sesscookieexp = 360
    sessautosave = True
    sessdir = '/tmp/smellsomething/sessions/'


    def __init__(self,):
        pass

class DevConfig(Config):
    host = 'localhost'
    port = 8787
    debug = True
    auto_reload = True
    tpl_path = './views/'

    dbname = 'smellsomethingdev'
    dbhost = 'localhost'
    dbuser = 'smellsomethingdev'
    dbpass = 'smellsomethingdev'

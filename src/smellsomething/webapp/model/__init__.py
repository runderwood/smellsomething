
class ModelError(Exception):
    pass

class Model:

    db = None

    _tablename = None
    _modelname = None

    DEF_LIMIT = 100

    def __init__(self,db=None):
        self.db = db

    def create(self,*args,**kwargs):
        return False

    def read(self,*args,**kwargs):
        return False

    def update(self,*args,**kwargs):
        return False

    def delete(self,*args,**kwargs):
        return False

    def list(self,*args,**kwargs):
        return False

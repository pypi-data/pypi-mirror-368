import yaml, uuid
from functools import lru_cache
from croniter import croniter
from ics import Event
from os.path import basename
from datetime import datetime as dt

class Schedule:

    def __init__(self,path):
        self.path = path 
        self.data = {}
    
    def transform_contact(self):
        self._load()
        cont = self.data
        birthday = cont.get("birthday")

        # todo
        self.data = {
                "active" : False
        }


    @lru_cache
    def _load(self):
        try:
            with open(self.path,'r') as f:
                self.data = yaml.safe_load(f.read())
        except Exception:
            pass

    @property
    def name(self):
        bn = basename(self.path)
        bn = bm.split('.')[:-1]
        bn = ".".join(bn)
        return bn

    @property
    @lru_cache
    def active(self):
        self._load()
        return self.data.get('active',False)
    
    @property
    @lru_cache
    def is_ics(self):
        ics = self.data.get('ics',{})
        ics_active = ics.get('active',False)
        return isinstance(ics,dict) and ics_active

    @property
    def cron_expr(self):
        return self.data.get('cron',None)

    @property
    @lru_cache
    def cron(self):
        if self.cron_expr is None:
            return

        if not croniter.is_valid(self.cron_expr):
            return

        return croniter(self.cron_expr,dt.now())
        
    def ics_days(self,days):
        _days = ['SU','MO','TU','WE','TH','FR','SA']
        return ','.join([_days[(int(d))] for d in days])

    @property
    @lru_cache
    def valid(self):
        return self.cron is not None \
                and self.is_ics \
                and self.cron_data is not None
    
    @property
    @lru_cache
    def cron_data(self):
        if self.cron is None:
            return None
    
        return crontier.expand(self.cron_expr)


    @property
    def event(self):
        e = Event()

        e.name = self.name
        e.uid = str(uuid.uuid4())
        e.description = self.data.get('description','undefined')
        e.priority = self.data.get('urgency',0)
        
        parts = self.cron_data[0]

        if parts[2] != ["*"] and parts[4] == ["*"]:
            e.extra.append("RRULE:FREQ=MONTHLY;BYMONTHDAY=" + ",".join(parts[2]))
        elif parts[4] != '*':
            e.extra.append("RRULE:FREQ=WEEKLY;BYDAY=" + self.ics_days(parts[4]))
        else:
            e.extra.append("RRULE:FREQ=DAILY")

        return e

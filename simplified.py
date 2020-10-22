import time 
from datetime import datetime, timedelta
import sched
from threading import Thread
from queue import Queue

def init_jobs(cls):
    cls.start_jobs()
    return cls

@init_jobs
class Jobs:

    running = {}

    @classmethod
    def start_jobs(cls):
        cls.jobs_scheduler = sched.scheduler(time.time, time.sleep)
        cls.jobs_queue = Queue(maxsize=100)
        cls.job_processor = Thread(target=cls.process_jobs, args=(cls.jobs_queue,))
        cls.job_processor.start()

    @classmethod
    def process_jobs(cls, q):
        while True:
            cls.jobs_scheduler.run()

    @classmethod
    def cancel_job(cls, job_id):
        try:
            cls.jobs_scheduler.cancel(cls.running[job_id])
            print('Successfully cancelled job, cleaning now...')
            cls.clean_job(job_id)

        except Exception as ex:
            print(ex)
    
    @classmethod
    def clean_job(cls, job_id):
        try:
            del cls.running[job_id]
            print('Deleted old job, Job.running now reading...', str(cls.running))
        
        except Exception as ex:
            print(ex)

    @classmethod
    def add(cls, schedTime, callback, payload, _abs=True):
        sched_id = ''
        job = cls(schedTime, callback, payload)
        if _abs:
            job_id = str(cls.jobs_scheduler.enterabs(job.schedTime, 1, job.callback, argument=(sched_id,), kwargs=job.payload))
        else:
            job_id = str(cls.jobs_scheduler.enter(job.schedTime, 1, job.callback, argument=(sched_id,), kwargs=job.payload))
        cls.running[job_id] = schedTime
        return job_id

    @staticmethod
    def deco_clean_job(fun):
        def wrapped(*args, **kwargs):
            print('cleaning job ', args[0])
            Jobs.clean_job(args[0])
            return fun(*args, **kwargs)
        return wrapped
    
    def __init__ (self, schedTime, callback, payload):
        self.setAt = datetime.now()
        self.payload = payload
        self.callback = callback
        self.schedTime = schedTime

    def readDate(date):
        return date.strftime("%d.%m.%Y %H:%M")

    @staticmethod
    def makeSchedTime(date_str):
        try: 
            d = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")-timedelta(hours=2)
            schedTime = time.mktime(d.timetuple()) + d.microsecond / 1E6
            return schedTime
        
        except ValueError as error:
            print('Bad date string')
            return False

p = {'a nice': 'payload'}

@Jobs.deco_clean_job
def cb(*arg, **p):
    print('calling back with', p)
    return p

Jobs.add(10, cb, p, _abs=False)
Jobs.add(12, cb, p, _abs=False)
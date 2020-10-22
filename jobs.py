from typing import Callable
from functools import partial
from datetime import datetime
from asyncio import set_event_loop, new_event_loop, run_coroutine_threadsafe
from threading import Thread

from post_jobs_requests import call_bot

""" 
CLASS
"""

def init_jobs(cls):
    cls.start_jobs()
    return cls

@init_jobs
class Jobs:

    running = {}

    """
    CLASS METHODS
    """

    @classmethod
    def start_jobs(cls):
        cls.loop = new_event_loop()
        cls.loop_thread = Thread(target=cls.offload_and_run, args=(cls.loop,))
        cls.loop_thread.start()

    @classmethod
    def offload_and_run(cls, loop):
        """ RUNS ON SIDE THREAD """
        set_event_loop(loop)
        loop.run_forever()
    
    @classmethod
    def schedule(cls, timetoSchedule, handler_callback:Callable, payload:dict) -> str:
        cancellation_voucher = hash(str(cls.loop.time()))
        instance = cls(
            timetoSchedule,
            handler_callback,
            payload,
            cancellation_voucher
        )
        cls.loop.call_soon_threadsafe(cls.set_task, instance)
        print('Just added job to the loop. Handing over cancellation voucher')
        return cancellation_voucher

    @classmethod
    def set_task(cls, instance:object):
        handle = cls.loop.call_later(
            instance.scheduledFor,
            Jobs.pack_callback(instance.handler_callback, instance.payload),
            cls.loop
        )
        cls.running[instance.cancellation_voucher] = handle
        

    @classmethod
    def unschedule(cls, cancellation_voucher:int) -> str:
        try:
            handle = cls.running[cancellation_voucher]
            handle.cancel()
            if handle._cancelled:
                return 'Cancelled scheduled.'
        except KeyError:
            return 'Failed to cancel with %s. Either the task is not scheduled or was already cancelled' % (str(cancellation_voucher))
    
    @classmethod
    def post_job(cls, *_, **payload:dict):
        return cls.schedule_async_callback(call_bot, payload)

    @classmethod
    def schedule_async_callback(cls, coro:Callable, payload:dict):
        run_coroutine_threadsafe(coro(payload), cls.loop)


    """
    STATIC
    """

    @staticmethod
    def diff(d:int, m:int, y:int, h:int, mm:int) -> int:
        target = datetime(y, m, d, h, mm)
        n = datetime.now()
        return (target-n).total_seconds()

    @staticmethod
    def pack_callback(handler_callback:Callable, payload:dict) -> partial:
        return partial(handler_callback, **payload)

    """
    JOBS
    """

    def __init__ (self, timeToSchedule, handler_callback:Callable, payload:dict, cancellation_voucher:int):
        self.setAt = datetime.now()
        self.cancellation_voucher = cancellation_voucher
        self.payload = payload
        self.handler_callback = handler_callback
        self.scheduledFor = Jobs.diff(*timeToSchedule) if isinstance (timeToSchedule, list) else timeToSchedule
 

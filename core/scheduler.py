import logging
import logging.config
logging.config.fileConfig('logging.conf')

import sched
import threading
import time
import datetime

class Scheduler:
    def __init__(self, format="%d/%m/%Y %H:%M:%S", delta_format="%H:%M:%S"):
        """
        Formats: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        """
        self.format = format
        self.delta_format = delta_format
        self.schedulers = []
        self.events = []
        self.threads = []

    def set_default_format(self, format):
        self.format = format

    def set_default_delta_format(self, delta_format):
        self.delta_format = delta_format

    def _parse_timedelta(self, repeat, delta_format=None):
        delta_format = self.delta_format if delta_format is None else delta_format
        try: 
            t = datetime.datetime.strptime(repeat, delta_format)
        except:
            logging.warning("Invalid time {} for format: {}".format(repeat, delta_format))
            return None
        return int(datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds())


    def add_from_now(self, t, func=None, repeat=None, limit=None, name=None, priority=1, delta_format=None, args=()):
        if func is None: 
            logging.warning("Function not passed")
            return
        if repeat is not None: wait_secs = self._parse_timedelta(repeat, delta_format)
        else: wait_secs = None

        scheduled_time = self._parse_timedelta(t, delta_format)
        if scheduled_time is None: return

        scheduler = sched.scheduler(time.time, time.sleep)
        self.schedulers.append(scheduler)

        self.events.append(scheduler.enterabs(scheduled_time + int(time.time()), priority, self._repeated_func, (func, wait_secs, limit, name, *args)))
        self.threads.append(threading.Thread(target=scheduler.run))
        return len(self.schedulers) - 1

    def add_at_specific_time(self, t, func=None, repeat=None, limit=None, name=None, priority=1, format=None, delta_format=None, args=()):
        if func is None: 
            logging.warning("Function not passed")
            return
        if repeat is not None: wait_secs = self._parse_timedelta(repeat, delta_format)
        else: wait_secs = None
    
        format = self.format if format is None else format
        try:
            scheduled_time = int(time.mktime(datetime.datetime.strptime(t, self.format).timetuple()))
        except:
            logging.warning("Invalid date {} for format: {}".format(t, format))
            return None

        scheduler = sched.scheduler(time.time, time.sleep)
        self.schedulers.append(scheduler)

        if time.time() > scheduled_time:
            logging.warning("Scheduled time already passed")
            return None

        self.events.append(scheduler.enterabs(scheduled_time, priority, self._repeated_func, (func, wait_secs, limit, name, *args)))
        self.threads.append(threading.Thread(target=scheduler.run))
        return len(self.schedulers) - 1


    def cancel(self, idx):
        self.schedulers[idx].cancel(self.events[idx])

    def cancell_all(self):
        for i in range(len(self.schedulers)): self.cancel(i)


    def __del__(self):
        try: self.cancell_all()
        except: pass

    def _repeated_func(self, func, wait_secs, limit, name, *args):
        if name is None: logging.info("Scheduled event runned")
        else: logging.info("{} runned".format(name))
        curr = 0
        while True:
            out = func(*args)
            curr += 1
            if wait_secs is None or (limit is not None and curr >= limit):
                break
            time.sleep(wait_secs)
        return out


    def start(self, func=None, *args):
        for thread in self.threads:
            thread.start()
        if func is not None and callable(func):
            func(*args) 
        for thread in self.threads:
            thread.join()
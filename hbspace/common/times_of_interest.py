import datetime
import numpy as np

class TimeOfInterest:
    def __init__(self, time_start: datetime.time,
                       time_end: datetime.time,
                       day_of_week=None):
        """
        time_start: Start time
        time_end: End time
        day_of_week: Array starting from Monday with values 1 or 0
        """
        self.time_start = time_start
        self.time_end   = time_end
        if day_of_week is None:
            self.day_of_week = np.ones(7)
        else:
            self.day_of_week = day_of_week

    def is_in(self, fixdatetime: datetime.datetime):
        return (self.day_of_week[fixdatetime.weekday()] == 1) and (fixdatetime.time() => self.time_start) and (fixdatetime.time() <= self.time_end)
                
import time
import requests
import hmac
import json
import arrow
import auth

BASE = "http://alarm.larsendt.com"
DAYS = 60 * 60 * 24
HOURS = 60 * 60
MINUTES = 60

class HTTPException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


def api_get(url, params):
    headers = {"Authorization": auth.make_hmac(params)}
    r = requests.get(BASE+url, data=params, headers=headers)
    if r.status_code != 200:
        raise HTTPException("Status was not 200! (%s)" % r.status_code)

    return json.loads(r.text)


class Alarm(object):
    def __init__(self, alarm_dict):
        self._dict = alarm_dict
        self._id = alarm_dict["id"]
        utc_seconds = -arrow.now().utcoffset().total_seconds()

        days_off = int(utc_seconds / DAYS)
        utc_seconds -= days_off * DAYS
        hours_off = int(utc_seconds / HOURS)
        utc_seconds -= hours_off * HOURS
        minutes_off = int(utc_seconds / MINUTES)
        utc_seconds -= minutes_off * MINUTES
        seconds_off = utc_seconds

        self._second = alarm_dict["second"] + seconds_off
        if self._second < 0:
            self._second += 60
            minutes_off -= 1
        elif self._second > 59:
            self._second -= 60
            minutes_off += 1

        self._minute = alarm_dict["minute"] + minutes_off
        if self._minute < 0:
            self._minute += 60
            hours_off -= 1
        elif self._minute > 59:
            self._minute -= 60
            hours_off += 1

        self._hour = alarm_dict["hour"] + hours_off
        if self._hour < 0:
            self._hour += 24
            days_off -= 1
        elif self._hour > 23:
            self._hour -= 24
            days_off += 1

        self._day = (alarm_dict["day"] + days_off) % 7

    def next_occurence(self):
        now = arrow.now("America/Denver")
        tt = now.timetuple()
        days_diff = self._day - ((tt.tm_wday + 1) % 7)
        hours_diff = self._hour - tt.tm_hour
        minutes_diff = self._minute - tt.tm_min
        seconds_diff = self._second - tt.tm_sec
        
        if seconds_diff < 0:
            seconds_diff += 60
            minutes_diff -= 1

        if minutes_diff < 0:
            minutes_diff += 60
            hours_diff -= 1

        if hours_diff < 0:
            hours_diff += 24
            days_diff -= 1

        if days_diff < 0:
            days_diff += 7

        total_diff = ((days_diff * DAYS) + (hours_diff * HOURS) + 
                (minutes_diff * MINUTES) + seconds_diff)
        return now.timestamp + total_diff


class AlarmScheduler(object):
    def __init__(self, alarm_function):
        self._alarm_function = alarm_function
        self._api_interval = 15
        self._alarms = []
        self._alarm_stack = []
        self._last_api_update = 0

    def update_alarms(self):
        alarm_objs = api_get("/api/alarms", {})
        self._alarms = []
        self._alarm_stack = []
        for alarm in alarm_objs["alarms"]:
            a = Alarm(alarm)
            self._alarms.append(a)
            self._alarm_stack.append(a.next_occurence())
        self._alarm_stack.sort()

    def loop(self):
        while True:
            now = int(time.time())
            if now - self._last_api_update > self._api_interval:
                print "updating alarms..."
                self.update_alarms()
                print "%d alarms" % len(self._alarms)
                self._last_api_update = now


            if len(self._alarm_stack) > 0:
                if self._alarm_stack[0] == now:
                    print "ALARM!"
                    self._alarm_function()
                    self._alarm_stack.pop(0)

            time.sleep(0.5)


if __name__ == "__main__":
    asched = AlarmScheduler()
    asched.loop()

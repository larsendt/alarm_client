#!/usr/bin/env python
import scheduler

def fn():
    print "WOASIOPFJASIOPHJFA"

s = scheduler.AlarmScheduler(fn)
s.loop()

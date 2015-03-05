#!/usr/bin/env python
import scheduler
import stepper

def fn():
    print "fn"
    stepper.run()

s = scheduler.AlarmScheduler(fn)
s.loop()

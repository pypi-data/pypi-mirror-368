#!/usr/local/bin/python3

import time
from datetime import datetime

import schedule


def job():
    print("I'm working...")


schedule.every(2).seconds.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)3
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)

while True:
    print(datetime.now().strftime("%H:%M:%S"))
    schedule.run_pending()
    time.sleep(4)

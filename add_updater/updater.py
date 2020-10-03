from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from add_updater import olx_scraper

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(olx_scraper.scraper, 'cron', day_of_week='mon-sun', hour='0-23', minute='0', second='0')
    scheduler.start()
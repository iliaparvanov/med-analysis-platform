from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path

def train_chest_xray_model():
    pass

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(train_chest_xray_model, 'interval', minutes=2)
    scheduler.start()

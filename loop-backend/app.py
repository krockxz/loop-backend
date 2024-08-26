from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd  # Import pandas

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

db = SQLAlchemy(app)

from models import StoreStatus, StoreBusinessHours, StoreTimezone  # Import models here

def load_csv_data():
  # Load StoreStatus data
  status_df = pd.read_csv('store_status.csv')
  status_df['timestamp_utc'] = pd.to_datetime(status_df['timestamp_utc'], format='mixed')
  status_df.to_sql('store_status', db.engine, if_exists='replace', index=False)

  # Load StoreBusinessHours data
  business_hours_df = pd.read_csv('store_business_hours.csv')
  business_hours_df.to_sql('store_business_hours', db.engine, if_exists='replace', index=False)

  # Load StoreTimezone data
  timezone_df = pd.read_csv('store_timezone.csv')
  timezone_df.to_sql('store_timezone', db.engine, if_exists='replace', index=False)

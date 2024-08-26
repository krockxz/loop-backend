from app import app, db
from celery import Celery
import pandas as pd
import pytz
from datetime import datetime, timedelta
import uuid
import os

from models import StoreStatus, StoreBusinessHours, StoreTimezone

celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

@celery.task(bind=True)
def generate_report(self, report_id):
  with app.app_context():  # Ensure the Flask app context is available
    max_timestamp = db.session.query(db.func.max(StoreStatus.timestamp_utc)).scalar()
    current_time = max_timestamp
    last_hour = current_time - timedelta(hours=1)
    last_day = current_time - timedelta(days=1)
    last_week = current_time - timedelta(weeks=1)

    report_data = []
    stores = db.session.query(StoreStatus.store_id).distinct()

    for store in stores:
      store_id = store[0]
      timezone = db.session.query(StoreTimezone).filter_by(store_id=store_id).first()
      timezone_str = timezone.timezone_str if timezone else 'America/Chicago'
      tz = pytz.timezone(timezone_str)

      def calculate_uptime_downtime(start_time, end_time):
        statuses = db.session.query(StoreStatus).filter(
            StoreStatus.store_id == store_id,
            StoreStatus.timestamp_utc.between(start_time, end_time)
        ).order_by(StoreStatus.timestamp_utc).all()

        uptime = 0
        downtime = 0

        if statuses:
          last_status = statuses[0].status
          last_time = statuses[0].timestamp_utc

          for status in statuses[1:]:
            time_diff = (status.timestamp_utc - last_time).total_seconds() / 60.0
            if last_status == 'active':
              uptime += time_diff
            else:
              downtime += time_diff

            last_status = status.status
            last_time = status.timestamp_utc

          time_diff = (end_time - last_time).total_seconds() / 60.0
          if last_status == 'active':
            uptime += time_diff
          else:
            downtime += time_diff

        return uptime, downtime

      uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(last_hour, current_time)
      uptime_last_day, downtime_last_day = calculate_uptime_downtime(last_day, current_time)
      uptime_last_week, downtime_last_week = calculate_uptime_downtime(last_week, current_time)

      report_data.append({
        'store_id': store_id,
        'uptime_last_hour': round(uptime_last_hour, 2),
        'uptime_last_day': round(uptime_last_day / 60, 2),
        'uptime_last_week': round(uptime_last_week / 60, 2),
        'downtime_last_hour': round(downtime_last_hour, 2),
        'downtime_last_day': round(downtime_last_day / 60, 2),
        'downtime_last_week': round(downtime_last_week / 60, 2)
      })

    report_df = pd.DataFrame(report_data)
    report_file = f"/tmp/{report_id}.csv"
    report_df.to_csv(report_file, index=False)

    return report_file

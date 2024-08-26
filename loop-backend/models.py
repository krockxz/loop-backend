from app import db

class StoreStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  store_id = db.Column(db.String, index=True)
  timestamp_utc = db.Column(db.DateTime)
  status = db.Column(db.String)

class StoreBusinessHours(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  store_id = db.Column(db.String, index=True)
  day_of_week = db.Column(db.Integer)
  start_time_local = db.Column(db.Time)
  end_time_local = db.Column(db.Time)

class StoreTimezone(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  store_id = db.Column(db.String, index=True)
  timezone_str = db.Column(db.String)

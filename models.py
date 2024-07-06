from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class VehicleData(db.Model):
    __tablename__ = 'vehicle_data'
    uuid = db.Column(db.String(36), primary_key=True)
    vehicle_type = db.Column(db.Enum('car', 'bus', 'truck','motorcycle','bicycle','person','truck'))
    timestamp = db.Column(db.DateTime)##ISO 8601形式でデータを格納するためdb.DateTimeは使わずに文字列で格納
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))

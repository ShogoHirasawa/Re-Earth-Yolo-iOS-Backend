from flask import Blueprint, jsonify, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, VehicleData, DeviceInfo, DeviceVehicle
from datetime import datetime, timedelta
from dateutil import parser
import uuid
import os
from dotenv import load_dotenv
import pytz  

load_dotenv()

# 環境変数からデータベースのユーザー名とパスワードを取得
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

# データベース設定
DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@localhost:3306/yolo_reearth'
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Blueprintの作成
bp = Blueprint('routes', __name__)

@bp.route('/api/recognition', methods=['POST'])
def receive_vehicle_data():
    print("Received request")
    session = Session()
    try:
        data = request.json
        print("Request JSON parsed:", data)
        device_uuid = data.get('uuid')
        records = data.get('data', [])
        print(f"UUID: {device_uuid}, Records: {len(records)}")

        # デバイス情報の確認と保存
        device = session.query(DeviceInfo).filter_by(device_id=device_uuid).first()
        if not device:
            device = DeviceInfo(device_id=device_uuid, name=f"Device {device_uuid}")
            session.add(device)
            session.commit()
            print("Device info saved:", device)

        for record in records:
            try:
                vehicle_data = VehicleData(
                    vehicle_type=record.get('obj_type'),
                    timestamp=parser.isoparse(record.get('timestamp')),
                    latitude=record.get('location').get('latitude'),
                    longitude=record.get('location').get('longitude')
                )
                session.add(vehicle_data)
                session.commit()
                print("Vehicle data saved:", vehicle_data)
            except ValueError as ve:
                print("ValueError occurred:", str(ve))
                return jsonify({"message": "Invalid data format.", "error": str(ve)}), 400

            device_vehicle = DeviceVehicle(device_id=device.id, vehicle_id=vehicle_data.id)
            session.add(device_vehicle)
            session.commit()
            print("DeviceVehicle record saved:", device_vehicle)

        return jsonify({"message": "Data successfully saved."}), 201
    except Exception as e:
        session.rollback()
        print("Error occurred:", str(e))
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500
    finally:
        session.close()
        print("Session closed")

@bp.route('/api/data/daily/', methods=['GET'])
def get_vehicle_data():
    session = Session()
    try:
        data = []
        # 現在時刻を日本時間で取得
        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)
        # 1時間前の時刻を計算
        one_hour_ago = now - timedelta(hours=1)
        # 直近1時間以内のデータをフィルタリング
        vehicles = session.query(VehicleData).filter(VehicleData.timestamp >= one_hour_ago).all()
        
        for vehicle in vehicles:
            # VehicleDataに関連するDeviceInfoを取得
            device_info = session.query(DeviceInfo).join(DeviceVehicle).filter(DeviceVehicle.vehicle_id == vehicle.id).first()
            data.append({
                'device_name': device_info.name if device_info else 'Unknown',
                'device_uuid': device_info.device_id if device_info else 'Unknown',
                'vehicle_type': vehicle.vehicle_type,
                'timestamp': vehicle.timestamp.isoformat(),
                'latitude': float(vehicle.latitude),
                'longitude': float(vehicle.longitude)
            })
        return jsonify(data), 200
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500
    finally:
        session.close()
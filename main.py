from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, VehicleData, DeviceInfo, DeviceVehicle
from datetime import datetime
from dateutil import parser
import uuid

app = Flask(__name__)

print("スタート")

# データベース設定
DATABASE_URI = 'mysql+pymysql://{user}:{pass}@localhost:3306/yolo_reearth'
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/api/recognition', methods=['POST'])
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
            vehicle_data = VehicleData(
                vehicle_type=record.get('obj_type'),
                timestamp=parser.isoparse(record.get('timestamp')),
                latitude=record.get('location').get('latitude'),
                longitude=record.get('location').get('longitude')
            )
            session.add(vehicle_data)
            session.commit()
            print("Vehicle data saved:", vehicle_data)

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

if __name__ == '__main__':
    app.run(debug=True)

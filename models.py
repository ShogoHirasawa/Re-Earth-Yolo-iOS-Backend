from sqlalchemy import create_engine, Column, String, Enum, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class VehicleData(Base):
    __tablename__ = 'vehicle_data'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_type = Column(Enum('car', 'bus', 'truck', 'motorcycle', 'bicycle', 'person'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    device_records = relationship('DeviceVehicle', back_populates='vehicle')

class DeviceInfo(Base):
    __tablename__ = 'device_info'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(36), nullable=False)
    device_id = Column(String(36), nullable=False)
    vehicle_records = relationship('DeviceVehicle', back_populates='device')

class DeviceVehicle(Base):
    __tablename__ = 'device_vehicle'
    device_id = Column(String(36), ForeignKey('device_info.id'), primary_key=True)
    vehicle_id = Column(String(36), ForeignKey('vehicle_data.id'), primary_key=True)
    device = relationship('DeviceInfo', back_populates='vehicle_records')
    vehicle = relationship('VehicleData', back_populates='device_records')

    def __repr__(self):
        return f"<DeviceVehicle(device_id='{self.device_id}', vehicle_id='{self.vehicle_id}')>"
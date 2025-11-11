from peewee import *
from typing import List, Optional
from datetime import datetime
from database import AttendanceRecord, Child, Group, JOIN, DoesNotExist


class AttendanceSettings:
    """Класс для работы с журналом посещаемости"""
    
    def add_attendance_record(self, child_id: int, date: str, status: str, notes: str = None):
        """Добавить запись о посещаемости"""
        AttendanceRecord.create(
            child=child_id,
            date=date,
            status=status,
            notes=notes
        )
    
    def update_attendance_record(self, child_id: int, date: str, status: str, notes: str = None):
        """Обновить запись о посещаемости"""
        try:
            record = AttendanceRecord.get(
                (AttendanceRecord.child == child_id) & 
                (AttendanceRecord.date == date)
            )
            record.status = status
            record.notes = notes
            record.updated_at = datetime.now()
            record.save()
        except DoesNotExist:
            self.add_attendance_record(child_id, date, status, notes)
    
    def get_attendance_by_group_and_date(self, group_id: int, date: str, children_settings):
        """Получить посещаемость группы на дату"""
        children = children_settings.get_children_by_group(group_id)
        result = []
        
        for child in children:
            try:
                record = AttendanceRecord.get(
                    (AttendanceRecord.child == child['child_id']) & 
                    (AttendanceRecord.date == date)
                )
                child_data = child.copy()
                child_data['status'] = record.status
                child_data['notes'] = record.notes or ''
                child_data['record_id'] = record.record_id
            except DoesNotExist:
                child_data = child.copy()
                child_data['status'] = 'Присутствует'
                child_data['notes'] = ''
                child_data['record_id'] = None
            
            result.append(child_data)
        
        return result
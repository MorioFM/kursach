"""
Настройки для работы с медицинскими картами
"""
from datetime import datetime


class MedicalCardSettings:
    """Класс для работы с медицинскими картами"""
    
    def get_medical_record(self, child_id: int):
        """Получить медицинскую карту ребёнка"""
        from database import MedicalRecord
        try:
            record = MedicalRecord.get(MedicalRecord.child == child_id)
            return {
                'record_id': record.record_id,
                'child_id': record.child.child_id,
                'blood_type': record.blood_type,
                'allergies': record.allergies,
                'chronic_diseases': record.chronic_diseases,
                'vaccinations': record.vaccinations,
                'height': record.height,
                'weight': record.weight,
                'doctor_notes': record.doctor_notes,
                'emergency_contact': record.emergency_contact,
                'last_checkup': record.last_checkup.strftime('%d-%m-%Y') if record.last_checkup else None
            }
        except:
            return None
    
    def create_or_update_medical_record(self, child_id: int, **kwargs):
        """Создать или обновить медицинскую карту"""
        from database import MedicalRecord
        
        # Преобразуем дату из строки
        if 'last_checkup' in kwargs and kwargs['last_checkup']:
            try:
                if '-' in kwargs['last_checkup'] and len(kwargs['last_checkup'].split('-')[0]) <= 2:
                    kwargs['last_checkup'] = datetime.strptime(kwargs['last_checkup'], '%d-%m-%Y').date()
                else:
                    kwargs['last_checkup'] = datetime.strptime(kwargs['last_checkup'], '%Y-%m-%d').date()
            except:
                kwargs['last_checkup'] = None
        
        kwargs['updated_at'] = datetime.now()
        
        try:
            record = MedicalRecord.get(MedicalRecord.child == child_id)
            for key, value in kwargs.items():
                setattr(record, key, value)
            record.save()
        except:
            MedicalRecord.create(child=child_id, **kwargs)
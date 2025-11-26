from peewee import *
from typing import List, Optional
from database import Teacher


class TeachersSettings:
    """Класс для работы с воспитателями в детском саду"""
    
    def add_teacher(self, last_name: str, first_name: str, middle_name: str = None,
                   phone: str = None, email: str = None, birth_date: str = None, address: str = None, education: str = None, experience: int = None) -> int:
        """
        Добавить нового воспитателя
        
        Args:
            last_name: фамилия
            first_name: имя
            middle_name: отчество (опционально)
            phone: телефон (опционально)
            email: email (опционально)
            birth_date: дата рождения (опционально)
            address: адрес (опционально)
            education: образование (опционально)
            experience: стаж работы (опционально)
        
        Returns:
            ID созданного воспитателя
        """
        teacher = Teacher.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            phone=phone,
            email=email,
            birth_date=birth_date,
            address=address,
            education=education,
            experience=experience
        )
        return teacher.teacher_id
    
    def get_all_teachers(self) -> List[dict]:
        """Получить список всех воспитателей"""
        teachers = Teacher.select().order_by(Teacher.last_name, Teacher.first_name)
        return [self._teacher_to_dict(teacher) for teacher in teachers]
    
    def get_teacher_by_id(self, teacher_id: int) -> Optional[dict]:
        """Получить информацию о воспитателе по ID"""
        try:
            teacher = Teacher.get_by_id(teacher_id)
            return self._teacher_to_dict(teacher)
        except DoesNotExist:
            return None
    
    def update_teacher(self, teacher_id: int, **kwargs):
        """Обновить информацию о воспитателе"""
        allowed_fields = {'last_name', 'first_name', 'middle_name', 'phone', 'email', 'birth_date', 'address', 'education', 'experience'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            Teacher.update(**updates).where(Teacher.teacher_id == teacher_id).execute()
    
    def delete_teacher(self, teacher_id: int) -> int:
        """Удалить воспитателя"""
        return Teacher.delete().where(Teacher.teacher_id == teacher_id).execute()
    
    def search_teachers(self, search_term: str) -> List[dict]:
        """Поиск воспитателей по ФИО, телефону или email"""
        if not search_term.strip():
            return self.get_all_teachers()
        
        search_pattern = f"%{search_term}%"
        teachers = (Teacher
                   .select()
                   .where(
                       (Teacher.last_name ** search_pattern) |
                       (Teacher.first_name ** search_pattern) |
                       (Teacher.middle_name ** search_pattern) |
                       (Teacher.phone ** search_pattern) |
                       (Teacher.email ** search_pattern)
                   )
                   .order_by(Teacher.last_name, Teacher.first_name))
        return [self._teacher_to_dict(teacher) for teacher in teachers]
    
    def _teacher_to_dict(self, teacher: Teacher) -> dict:
        """Преобразовать модель воспитателя в словарь"""
        return {
            'teacher_id': teacher.teacher_id,
            'last_name': teacher.last_name,
            'first_name': teacher.first_name,
            'middle_name': teacher.middle_name or '',
            'full_name': f"{teacher.last_name} {teacher.first_name}" + 
                        (f" {teacher.middle_name}" if teacher.middle_name else ""),
            'phone': teacher.phone or '',
            'email': teacher.email or '',
            'birth_date': getattr(teacher, 'birth_date', None) or '',
            'address': getattr(teacher, 'address', None) or '',
            'education': getattr(teacher, 'education', None) or '',
            'experience': getattr(teacher, 'experience', None),
            'created_at': teacher.created_at.isoformat() if teacher.created_at else None
        }
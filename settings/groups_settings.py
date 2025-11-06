from peewee import *
from typing import List, Optional
from database import Group, Teacher, Child, JOIN


class GroupsSettings:
    """Класс для работы с группами в детском саду"""
    
    def add_group(self, group_name: str, age_category: str, teacher_id: Optional[int] = None) -> int:
        """
        Добавить новую группу
        
        Args:
            group_name: название группы
            age_category: возрастная категория
            teacher_id: ID воспитателя (опционально)
        
        Returns:
            ID созданной группы
        """
        group = Group.create(
            group_name=group_name,
            age_category=age_category,
            teacher=teacher_id
        )
        return group.group_id
    
    def get_all_groups(self) -> List[dict]:
        """Получить список всех групп"""
        groups = (Group
                 .select(Group, Teacher)
                 .join(Teacher, JOIN.LEFT_OUTER)
                 .order_by(Group.group_name))
        return [self._group_to_dict(group) for group in groups]
    
    def get_group_by_id(self, group_id: int) -> Optional[dict]:
        """Получить информацию о группе по ID"""
        try:
            group = Group.get_by_id(group_id)
            return self._group_to_dict(group)
        except DoesNotExist:
            return None
    
    def update_group(self, group_id: int, **kwargs):
        """Обновить информацию о группе"""
        updates = {}
        if 'group_name' in kwargs:
            updates['group_name'] = kwargs['group_name']
        if 'age_category' in kwargs:
            updates['age_category'] = kwargs['age_category']
        if 'teacher_id' in kwargs:
            updates['teacher'] = kwargs['teacher_id']
        
        if updates:
            Group.update(**updates).where(Group.group_id == group_id).execute()
    
    def delete_group(self, group_id: int) -> int:
        """Удалить группу"""
        # Открепляем всех детей от группы
        Child.update(group=None).where(Child.group == group_id).execute()
        return Group.delete().where(Group.group_id == group_id).execute()
    
    def _group_to_dict(self, group: Group) -> dict:
        """Преобразовать модель группы в словарь"""
        result = {
            'group_id': group.group_id,
            'group_name': group.group_name,
            'age_category': group.age_category,
            'teacher_id': group.teacher_id if group.teacher else None,
            'created_at': group.created_at.isoformat() if group.created_at else None
        }
        
        if hasattr(group, 'teacher') and group.teacher:
            result['teacher_name'] = f"{group.teacher.last_name} {group.teacher.first_name}"
            if group.teacher.middle_name:
                result['teacher_name'] += f" {group.teacher.middle_name}"
        
        return result
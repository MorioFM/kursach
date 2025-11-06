from peewee import *
from typing import List, Optional
from database import Child, Group, JOIN


class ChildrenSettings:
    """Класс для работы с детьми в детском саду"""
    
    def add_child(self, last_name: str, first_name: str, middle_name: str,
                  birth_date: str, gender: str, group_id: int, 
                  enrollment_date: str) -> int:
        """
        Добавить нового ребенка
        
        Args:
            last_name: фамилия
            first_name: имя
            middle_name: отчество
            birth_date: дата рождения (формат: YYYY-MM-DD)
            gender: пол (М или Ж)
            group_id: ID группы
            enrollment_date: дата зачисления (формат: YYYY-MM-DD)
        
        Returns:
            ID созданной записи
        """
        child = Child.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            birth_date=birth_date,
            gender=gender,
            group=group_id,
            enrollment_date=enrollment_date
        )
        return child.child_id
    
    def get_all_children(self) -> List[dict]:
        """Получить список всех детей"""
        children = (Child
                   .select(Child, Group)
                   .join(Group, JOIN.LEFT_OUTER)
                   .order_by(Child.last_name, Child.first_name))
        return [self._child_to_dict(child) for child in children]
    
    def get_child_by_id(self, child_id: int) -> Optional[dict]:
        """Получить информацию о ребенке по ID"""
        try:
            child = (Child
                    .select(Child, Group)
                    .join(Group, JOIN.LEFT_OUTER)
                    .where(Child.child_id == child_id)
                    .get())
            return self._child_to_dict(child)
        except DoesNotExist:
            return None
    
    def get_children_by_group(self, group_id: int) -> List[dict]:
        """Получить список детей в группе"""
        children = (Child
                   .select()
                   .where(Child.group == group_id)
                   .order_by(Child.last_name, Child.first_name))
        return [self._child_to_dict(child) for child in children]
    
    def search_children(self, search_term: str) -> List[dict]:
        """Поиск детей по фамилии или имени"""
        if not search_term.strip():
            return self.get_all_children()
        
        search_pattern = f"%{search_term}%"
        children = (Child
                   .select(Child, Group)
                   .join(Group, JOIN.LEFT_OUTER)
                   .where(
                       (Child.last_name ** search_pattern) |
                       (Child.first_name ** search_pattern)
                   )
                   .order_by(Child.last_name, Child.first_name))
        return [self._child_to_dict(child) for child in children]
    
    def update_child(self, child_id: int, **kwargs):
        """
        Обновить информацию о ребенке
        
        Args:
            child_id: ID ребенка
            **kwargs: поля для обновления (last_name, first_name, middle_name, 
                     birth_date, gender, group_id, enrollment_date)
        """
        allowed_fields = ['last_name', 'first_name', 'middle_name', 
                         'birth_date', 'gender', 'enrollment_date']
        
        updates = {}
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates[field] = value
            elif field == 'group_id':  # Убрал проверку value is not None
                updates['group'] = value
        
        if updates:
            Child.update(**updates).where(Child.child_id == child_id).execute()
    
    def delete_child(self, child_id: int) -> int:
        """Удалить ребенка из базы данных"""
        return Child.delete().where(Child.child_id == child_id).execute()
    
    def transfer_child_to_group(self, child_id: int, new_group_id: int):
        """Перевести ребенка в другую группу"""
        self.update_child(child_id, group_id=new_group_id)
    
    def bulk_transfer_children(self, child_ids: List[int], new_group_id: int) -> int:
        """Массовый перевод детей в группу"""
        return (Child
                .update(group=new_group_id)
                .where(Child.child_id.in_(child_ids))
                .execute())
    
    def get_children_without_group(self) -> List[dict]:
        """Получить детей без группы"""
        children = (Child
                   .select()
                   .where(Child.group.is_null())
                   .order_by(Child.last_name, Child.first_name))
        return [self._child_to_dict(child) for child in children]
    
    def _child_to_dict(self, child: Child) -> dict:
        """Преобразовать модель ребенка в словарь"""
        result = {
            'child_id': child.child_id,
            'last_name': child.last_name,
            'first_name': child.first_name,
            'middle_name': child.middle_name or '',
            'birth_date': child.birth_date.isoformat() if hasattr(child.birth_date, 'isoformat') else str(child.birth_date),
            'gender': child.gender,
            'group_id': child.group_id if child.group else None,
            'enrollment_date': child.enrollment_date.isoformat() if hasattr(child.enrollment_date, 'isoformat') else str(child.enrollment_date),
            'created_at': child.created_at.isoformat() if child.created_at else None
        }
        
        if hasattr(child, 'group') and child.group:
            result['group_name'] = child.group.group_name
            result['age_category'] = child.group.age_category
        
        return result
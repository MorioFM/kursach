from peewee import *
from typing import List, Optional
from database import Parent


class ParentsSettings:
    """Класс для работы с родителями в детском саду"""
    
    def add_parent(self, last_name: str, first_name: str, middle_name: str = None,
                   phone: str = None, email: str = None, address: str = None) -> int:
        """
        Добавить нового родителя
        
        Args:
            last_name: фамилия
            first_name: имя
            middle_name: отчество (опционально)
            phone: телефон (опционально)
            email: email (опционально)
            address: адрес (опционально)
        
        Returns:
            ID созданного родителя
        """
        parent = Parent.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            phone=phone,
            email=email,
            address=address
        )
        return parent.parent_id
    
    def get_all_parents(self) -> List[dict]:
        """Получить список всех родителей"""
        parents = Parent.select().order_by(Parent.last_name, Parent.first_name)
        return [self._parent_to_dict(parent) for parent in parents]
    
    def get_parent_by_id(self, parent_id: int) -> Optional[dict]:
        """Получить информацию о родителе по ID"""
        try:
            parent = Parent.get_by_id(parent_id)
            return self._parent_to_dict(parent)
        except DoesNotExist:
            return None
    
    def update_parent(self, parent_id: int, **kwargs):
        """Обновить информацию о родителе"""
        allowed_fields = {'last_name', 'first_name', 'middle_name', 'phone', 'email', 'address'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            Parent.update(**updates).where(Parent.parent_id == parent_id).execute()
    
    def delete_parent(self, parent_id: int) -> int:
        """Удалить родителя"""
        return Parent.delete().where(Parent.parent_id == parent_id).execute()
    
    def search_parents(self, search_term: str) -> List[dict]:
        """Поиск родителей по ФИО, телефону или email"""
        if not search_term.strip():
            return self.get_all_parents()
        
        search_pattern = f"%{search_term}%"
        parents = (Parent
                   .select()
                   .where(
                       (Parent.last_name ** search_pattern) |
                       (Parent.first_name ** search_pattern) |
                       (Parent.middle_name ** search_pattern) |
                       (Parent.phone ** search_pattern) |
                       (Parent.email ** search_pattern)
                   )
                   .order_by(Parent.last_name, Parent.first_name))
        return [self._parent_to_dict(parent) for parent in parents]
    
    def _parent_to_dict(self, parent: Parent) -> dict:
        """Преобразовать модель родителя в словарь"""
        return {
            'parent_id': parent.parent_id,
            'last_name': parent.last_name,
            'first_name': parent.first_name,
            'middle_name': parent.middle_name or '',
            'full_name': f"{parent.last_name} {parent.first_name}" + 
                        (f" {parent.middle_name}" if parent.middle_name else ""),
            'phone': parent.phone or '',
            'email': parent.email or '',
            'address': parent.address or '',
            'created_at': parent.created_at.isoformat() if parent.created_at else None
        }
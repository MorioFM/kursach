from peewee import *
from datetime import datetime
from typing import List, Optional

# Инициализация базы данных
db = SqliteDatabase(None)


class BaseModel(Model):
    """Базовая модель для всех таблиц"""
    class Meta:
        database = db


class Teacher(BaseModel):
    """Модель воспитателя"""
    teacher_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'teachers'


class Group(BaseModel):
    """Модель группы детского сада"""
    group_id = AutoField(primary_key=True)
    group_name = CharField(null=False)
    age_category = CharField(null=False)
    teacher = ForeignKeyField(Teacher, backref='groups', null=True, column_name='teacher_id')
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'groups'


class Parent(BaseModel):
    """Модель родителя"""
    parent_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    address = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'parents'


class Child(BaseModel):
    """Модель ребенка"""
    child_id = AutoField(primary_key=True)
    last_name = CharField(null=False)
    first_name = CharField(null=False)
    middle_name = CharField(null=True)
    birth_date = DateField(null=False)
    gender = CharField(null=False, constraints=[Check("gender IN ('М', 'Ж')")])
    group = ForeignKeyField(Group, backref='children', null=True, column_name='group_id')
    enrollment_date = DateField(null=False)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'children'
        indexes = (
            (('last_name', 'first_name'), False),
        )


class ParentChild(BaseModel):
    """Модель связи родителя и ребенка"""
    parent = ForeignKeyField(Parent, backref='parent_children', column_name='parent_id')
    child = ForeignKeyField(Child, backref='child_parents', column_name='child_id')
    relationship = CharField(null=False)  # Мама, Папа, Опекун и т.д.
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'parent_child'
        primary_key = CompositeKey('parent', 'child')


class KindergartenDB:
    """Класс для работы с базой данных детского сада через Peewee ORM"""
    
    def __init__(self, db_path: str = "kindergarten.db"):
        """
        Инициализация подключения к базе данных
        
        Args:
            db_path: путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.connection = None
        from settings.children_settings import ChildrenSettings
        from settings.teachers_settings import TeachersSettings
        from settings.parents_settings import ParentsSettings
        from settings.groups_settings import GroupsSettings
        self._children_settings = ChildrenSettings()
        self._teachers_settings = TeachersSettings()
        self._parents_settings = ParentsSettings()
        self._groups_settings = GroupsSettings()
    
    def connect(self):
        """Установить соединение с базой данных"""
        db.init(self.db_path)
        db.connect()
        self.connection = db
        return self.connection
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if db and not db.is_closed():
            db.close()
    
    def create_tables(self):
        """Создать таблицы в базе данных"""
        db.create_tables([Teacher, Group, Parent, Child, ParentChild])
        print("Tables created successfully")
    
    # === РАБОТА С ВОСПИТАТЕЛЯМИ ===
    
    def add_teacher(self, *args, **kwargs):
        return self._teachers_settings.add_teacher(*args, **kwargs)
    
    def get_all_teachers(self):
        return self._teachers_settings.get_all_teachers()
    
    def get_teacher_by_id(self, teacher_id: int):
        return self._teachers_settings.get_teacher_by_id(teacher_id)
    
    def update_teacher(self, teacher_id: int, **kwargs):
        return self._teachers_settings.update_teacher(teacher_id, **kwargs)
    
    def delete_teacher(self, teacher_id: int):
        return self._teachers_settings.delete_teacher(teacher_id)
    
    def search_teachers(self, search_term: str):
        return self._teachers_settings.search_teachers(search_term)
    
    # === РАБОТА С РОДИТЕЛЯМИ ===
    
    def add_parent(self, *args, **kwargs):
        return self._parents_settings.add_parent(*args, **kwargs)
    
    def get_all_parents(self):
        return self._parents_settings.get_all_parents()
    
    def get_parent_by_id(self, parent_id: int):
        return self._parents_settings.get_parent_by_id(parent_id)
    
    def update_parent(self, parent_id: int, **kwargs):
        return self._parents_settings.update_parent(parent_id, **kwargs)
    
    def delete_parent(self, parent_id: int):
        return self._parents_settings.delete_parent(parent_id)
    
    def search_parents(self, search_term: str):
        return self._parents_settings.search_parents(search_term)
    
    # === РАБОТА СО СВЯЗЯМИ РОДИТЕЛЬ-РЕБЕНОК ===
    
    def add_parent_child_relation(self, parent_id: int, child_id: int, relationship: str):
        """Добавить связь родитель-ребенок"""
        ParentChild.create(
            parent=parent_id,
            child=child_id,
            relationship=relationship
        )
    
    def remove_parent_child_relation(self, parent_id: int, child_id: int):
        """Удалить связь родитель-ребенок"""
        ParentChild.delete().where(
            (ParentChild.parent == parent_id) & 
            (ParentChild.child == child_id)
        ).execute()
    
    def get_children_by_parent(self, parent_id: int):
        """Получить детей родителя"""
        relations = (ParentChild
                    .select(ParentChild, Child, Group)
                    .join(Child)
                    .join(Group, JOIN.LEFT_OUTER)
                    .where(ParentChild.parent == parent_id))
        
        result = []
        for relation in relations:
            child_data = self._children_settings._child_to_dict(relation.child)
            child_data['relationship'] = relation.relationship
            result.append(child_data)
        return result
    
    def get_parents_by_child(self, child_id: int):
        """Получить родителей ребенка"""
        relations = (ParentChild
                    .select(ParentChild, Parent)
                    .join(Parent)
                    .where(ParentChild.child == child_id))
        
        result = []
        for relation in relations:
            parent_data = self._parents_settings._parent_to_dict(relation.parent)
            parent_data['relationship'] = relation.relationship
            result.append(parent_data)
        return result
    
    # === РАБОТА С ГРУППАМИ ===
    
    def add_group(self, *args, **kwargs):
        return self._groups_settings.add_group(*args, **kwargs)
    
    def get_all_groups(self):
        return self._groups_settings.get_all_groups()
    
    def get_group_by_id(self, group_id: int):
        return self._groups_settings.get_group_by_id(group_id)
    
    def update_group(self, group_id: int, **kwargs):
        return self._groups_settings.update_group(group_id, **kwargs)
    
    def delete_group(self, group_id: int):
        return self._groups_settings.delete_group(group_id)
    
    # === РАБОТА С ДЕТЬМИ ===
    
    def add_child(self, *args, **kwargs):
        return self._children_settings.add_child(*args, **kwargs)
    
    def get_all_children(self):
        return self._children_settings.get_all_children()
    
    def get_child_by_id(self, child_id: int):
        return self._children_settings.get_child_by_id(child_id)
    
    def get_children_by_group(self, group_id: int):
        return self._children_settings.get_children_by_group(group_id)
    
    def search_children(self, search_term: str):
        return self._children_settings.search_children(search_term)
    
    def update_child(self, child_id: int, **kwargs):
        return self._children_settings.update_child(child_id, **kwargs)
    
    def delete_child(self, child_id: int):
        return self._children_settings.delete_child(child_id)
    
    def transfer_child_to_group(self, child_id: int, new_group_id: int):
        return self._children_settings.transfer_child_to_group(child_id, new_group_id)
    
    def bulk_transfer_children(self, child_ids: List[int], new_group_id: int):
        return self._children_settings.bulk_transfer_children(child_ids, new_group_id)
    
    def get_children_without_group(self):
        return self._children_settings.get_children_without_group()
    

    

    

    

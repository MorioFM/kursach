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
        db.create_tables([Teacher, Group, Child])
        print("Tables created successfully")
    
    # === РАБОТА С ВОСПИТАТЕЛЯМИ ===
    
    def add_teacher(self, last_name: str, first_name: str, middle_name: str = None,
                   phone: str = None, email: str = None) -> int:
        """
        Добавить нового воспитателя
        
        Args:
            last_name: фамилия
            first_name: имя
            middle_name: отчество (опционально)
            phone: телефон (опционально)
            email: email (опционально)
        
        Returns:
            ID созданного воспитателя
        """
        teacher = Teacher.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            phone=phone,
            email=email
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
        """
        Обновить информацию о воспитателе
        
        Args:
            teacher_id: ID воспитателя
            **kwargs: поля для обновления
        """
        allowed_fields = ['last_name', 'first_name', 'middle_name', 'phone', 'email']
        
        updates = {}
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates[field] = value
        
        if updates:
            Teacher.update(**updates).where(Teacher.teacher_id == teacher_id).execute()
    
    def delete_teacher(self, teacher_id: int):
        """Удалить воспитателя"""
        Teacher.delete().where(Teacher.teacher_id == teacher_id).execute()
    
    def search_teachers(self, search_term: str) -> List[dict]:
        """
        Поиск воспитателей по ФИО, телефону или email
        
        Args:
            search_term: строка для поиска
        
        Returns:
            список найденных воспитателей
        """
        teachers = (Teacher
                   .select()
                   .where(
                       (Teacher.last_name.contains(search_term)) |
                       (Teacher.first_name.contains(search_term)) |
                       (Teacher.middle_name.contains(search_term)) |
                       (Teacher.phone.contains(search_term)) |
                       (Teacher.email.contains(search_term))
                   )
                   .order_by(Teacher.last_name, Teacher.first_name))
        return [self._teacher_to_dict(teacher) for teacher in teachers]
    
    # === РАБОТА С ГРУППАМИ ===
    
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
    
    def update_group(self, group_id: int, group_name: str = None, 
                    age_category: str = None, teacher_id: int = None):
        """Обновить информацию о группе"""
        query = Group.update()
        updates = {}
        
        if group_name is not None:
            updates['group_name'] = group_name
        if age_category is not None:
            updates['age_category'] = age_category
        if teacher_id is not None:
            updates['teacher'] = teacher_id
        
        if updates:
            Group.update(**updates).where(Group.group_id == group_id).execute()
    
    def delete_group(self, group_id: int):
        """Удалить группу"""
        Group.delete().where(Group.group_id == group_id).execute()
    
    # === РАБОТА С ДЕТЬМИ ===
    
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
        """
        Поиск детей по фамилии или имени
        
        Args:
            search_term: строка для поиска
        
        Returns:
            список найденных детей
        """
        children = (Child
                   .select(Child, Group)
                   .join(Group, JOIN.LEFT_OUTER)
                   .where(
                       (Child.last_name.contains(search_term)) |
                       (Child.first_name.contains(search_term))
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
    
    def delete_child(self, child_id: int):
        """Удалить ребенка из базы данных"""
        Child.delete().where(Child.child_id == child_id).execute()
    
    def transfer_child_to_group(self, child_id: int, new_group_id: int):
        """Перевести ребенка в другую группу"""
        self.update_child(child_id, group_id=new_group_id)
    
    # === СТАТИСТИКА ===
    
    def get_group_statistics(self) -> List[dict]:
        """Получить статистику по группам"""
        query = (Group
                .select(
                    Group.group_id,
                    Group.group_name,
                    Group.age_category,
                    fn.COUNT(Child.child_id).alias('children_count'),
                    fn.SUM(Case(None, [(Child.gender == 'М', 1)], 0)).alias('boys_count'),
                    fn.SUM(Case(None, [(Child.gender == 'Ж', 1)], 0)).alias('girls_count')
                )
                .join(Child, JOIN.LEFT_OUTER)
                .group_by(Group.group_id, Group.group_name, Group.age_category)
                .order_by(Group.group_name))
        
        return [
            {
                'group_id': row.group_id,
                'group_name': row.group_name,
                'age_category': row.age_category,
                'children_count': row.children_count or 0,
                'boys_count': row.boys_count or 0,
                'girls_count': row.girls_count or 0
            }
            for row in query
        ]
    
    def get_children_by_age(self, min_age: int, max_age: int) -> List[dict]:
        """
        Получить детей в определенном возрастном диапазоне
        
        Args:
            min_age: минимальный возраст
            max_age: максимальный возраст
        
        Returns:
            список детей
        """
        # Вычисляем возраст через SQL функцию
        age_expr = fn.CAST(
            (fn.julianday('now') - fn.julianday(Child.birth_date)) / 365.25,
            'INTEGER'
        )
        
        children = (Child
                   .select(Child, Group, age_expr.alias('age'))
                   .join(Group, JOIN.LEFT_OUTER)
                   .where(age_expr.between(min_age, max_age))
                   .order_by(Child.birth_date.desc()))
        
        result = []
        for child in children:
            child_dict = self._child_to_dict(child)
            child_dict['age'] = child.age
            result.append(child_dict)
        
        return result
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
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
    
    def _child_to_dict(self, child: Child) -> dict:
        """Преобразовать модель ребенка в словарь"""
        result = {
            'child_id': child.child_id,
            'last_name': child.last_name,
            'first_name': child.first_name,
            'middle_name': child.middle_name,
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
    
    def _teacher_to_dict(self, teacher: Teacher) -> dict:
        """Преобразовать модель воспитателя в словарь"""
        return {
            'teacher_id': teacher.teacher_id,
            'last_name': teacher.last_name,
            'first_name': teacher.first_name,
            'middle_name': teacher.middle_name,
            'full_name': f"{teacher.last_name} {teacher.first_name}" + 
                        (f" {teacher.middle_name}" if teacher.middle_name else ""),
            'phone': teacher.phone,
            'email': teacher.email,
            'created_at': teacher.created_at.isoformat() if teacher.created_at else None
        }
    
    def get_statistics(self) -> dict:
        """Получить общую статистику"""
        total_children = Child.select().count()
        total_groups = Group.select().count()
        total_teachers = Teacher.select().count()
        
        # Вычисляем средний возраст
        if total_children > 0:
            # Используем SQL для вычисления среднего возраста
            age_expr = (fn.julianday('now') - fn.julianday(Child.birth_date)) / 365.25
            avg_age_result = Child.select(fn.AVG(age_expr)).scalar()
            average_age = avg_age_result if avg_age_result else 0
        else:
            average_age = 0
        
        return {
            'total_children': total_children,
            'total_groups': total_groups,
            'total_teachers': total_teachers,
            'average_age': round(average_age, 1)
        }
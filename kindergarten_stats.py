"""
Модуль для работы со статистикой детского сада
"""
from typing import List
from peewee import fn, Case, JOIN


# Импортируем модели локально чтобы избежать циклических зависимостей
def get_models():
    from database import Child, Group, Teacher
    return Child, Group, Teacher


class KindergartenStatistics:
    """Класс для получения статистики детского сада"""
    
    @staticmethod
    def get_group_statistics() -> List[dict]:
        """Получить статистику по группам"""
        Child, Group, Teacher = get_models()
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
    
    @staticmethod
    def get_children_by_age(min_age: int, max_age: int) -> List[dict]:
        """
        Получить детей в определенном возрастном диапазоне
        
        Args:
            min_age: минимальный возраст
            max_age: максимальный возраст
        
        Returns:
            список детей
        """
        Child, Group, Teacher = get_models()
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
            child_dict = {
                'child_id': child.child_id,
                'last_name': child.last_name,
                'first_name': child.first_name,
                'middle_name': child.middle_name,
                'birth_date': child.birth_date.isoformat() if hasattr(child.birth_date, 'isoformat') else str(child.birth_date),
                'gender': child.gender,
                'group_id': child.group_id if child.group else None,
                'enrollment_date': child.enrollment_date.isoformat() if hasattr(child.enrollment_date, 'isoformat') else str(child.enrollment_date),
                'age': child.age
            }
            
            if hasattr(child, 'group') and child.group:
                child_dict['group_name'] = child.group.group_name
                child_dict['age_category'] = child.group.age_category
            
            result.append(child_dict)
        
        return result
    
    @staticmethod
    def get_general_statistics() -> dict:
        """Получить общую статистику"""
        Child, Group, Teacher = get_models()
        # Оптимизированный запрос для получения всей статистики за один запрос
        age_expr = (fn.julianday('now') - fn.julianday(Child.birth_date)) / 365.25
        
        stats = (Child
                .select(
                    fn.COUNT(Child.child_id).alias('total_children'),
                    fn.AVG(age_expr).alias('average_age')
                )
                .scalar(as_tuple=True))
        
        total_children, average_age = stats if stats[0] else (0, 0)
        
        # Отдельные запросы для групп и воспитателей
        total_groups = Group.select().count()
        total_teachers = Teacher.select().count()
        
        return {
            'total_children': total_children,
            'total_groups': total_groups,
            'total_teachers': total_teachers,
            'average_age': round(average_age or 0, 1)
        }
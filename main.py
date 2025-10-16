"""
Главный файл приложения
"""
import flet as ft
from database import KindergartenDB
from view.children_view import ChildrenView
from view.groups_view import GroupsView
from view.teachers_view import TeachersView
from settings.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, DATABASE_NAME


def main(page: ft.Page):
    """Главная функция приложения"""
    page.title = APP_TITLE
    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Инициализация базы данных
    db = KindergartenDB(DATABASE_NAME)
    db.connect()
    db.create_tables()
    
    # Контейнер для текущего представления
    content_container = ft.Container(expand=True)
    
    # Создаем представления
    children_view = ChildrenView(db, lambda: refresh_current_view())
    groups_view = GroupsView(db, lambda: refresh_current_view())
    teachers_view = TeachersView(db, lambda: refresh_current_view())
    
    # Текущее представление
    current_view = [children_view]
    
    def refresh_current_view():
        """Обновить текущее представление"""
        if current_view[0] == children_view:
            children_view.load_children()
        elif current_view[0] == groups_view:
            groups_view.load_groups()
        elif current_view[0] == teachers_view:
            teachers_view.load_teachers()
    
    def switch_view(view):
        """Переключить представление"""
        current_view[0] = view
        content_container.content = view
        
        # Загрузить данные для представления
        if view == children_view:
            children_view.load_children()
        elif view == groups_view:
            groups_view.load_groups()
        elif view == teachers_view:
            teachers_view.load_teachers()
        
        page.update()
    
    # Боковое меню
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHILD_CARE_OUTLINED,
                selected_icon=ft.Icons.CHILD_CARE,
                label="Дети",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.GROUPS_OUTLINED,
                selected_icon=ft.Icons.GROUPS,
                label="Группы",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINED,
                selected_icon=ft.Icons.PERSON,
                label="Воспитатели",
            ),
        ],
        on_change=lambda e: switch_view(
            children_view if e.control.selected_index == 0 
            else groups_view if e.control.selected_index == 1
            else teachers_view
        ),
    )
    
    # Основной layout
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            content_container,
        ], expand=True)
    )
    
    # Загружаем начальное представление
    switch_view(children_view)


if __name__ == "__main__":
    ft.app(target=main)

"""
Главный файл приложения
"""
import flet as ft
from database import KindergartenDB
from view.children_view import ChildrenView
from view.groups_view import GroupsView
from view.teachers_view import TeachersView
from view.parents_view import ParentsView
from view.attendance_view import AttendanceView
from settings.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, DATABASE_NAME


def main(page: ft.Page):
    """Главная функция приложения"""
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # Создаем контейнер для заголовка с динамическим цветом
    header_container = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=lambda e: page.open(page.drawer),
                ),
                ft.Text(APP_TITLE, size=20, weight="bold"),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        padding=10
    )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        # Обновляем цвет заголовка в зависимости от темы
        header_container.bgcolor = ft.Colors.ON_SURFACE_VARIANT if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.ON_SURFACE_VARIANT
        page.update()

    theme_switch = ft.Switch(
        label="Тема приложения",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme
    )
    
    # Инициализация базы данных
    db = KindergartenDB(DATABASE_NAME)
    db.connect()
    db.create_tables()
    
    # Контейнер для текущего представления
    content_container = ft.Container(expand=True)
    
    # Создаем представления
    children_view = ChildrenView(db, lambda: refresh_current_view(), page)
    groups_view = GroupsView(db, lambda: refresh_current_view())
    teachers_view = TeachersView(db, lambda: refresh_current_view())
    parents_view = ParentsView(db, lambda: refresh_current_view(), page)
    attendance_view = AttendanceView(db, lambda: refresh_current_view(), page)
    
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
        elif current_view[0] == parents_view:
            parents_view.load_parents()
        elif current_view[0] == attendance_view:
            attendance_view.load_attendance()
    
    def switch_view(view, e=None):
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
        elif view == parents_view:
            parents_view.load_parents()
        elif view == attendance_view:
            attendance_view.load_attendance()
        
        page.drawer.open = False
        page.update()



    def handle_change(e):
        page.drawer.open = False
        page.update()
    
    page.drawer = ft.NavigationDrawer(
        on_change=handle_change,
        controls=[
            ft.Container(height=20),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.CHILD_CARE_OUTLINED),
                title=ft.Text("Дети"),
                on_click=lambda e: switch_view(children_view, e)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.GROUPS_OUTLINED),
                title=ft.Text("Группы"),
                on_click=lambda e: switch_view(groups_view, e)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON_OUTLINED),
                title=ft.Text("Воспитатели"),
                on_click=lambda e: switch_view(teachers_view, e)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.FAMILY_RESTROOM_OUTLINED),
                title=ft.Text("Родители"),
                on_click=lambda e: switch_view(parents_view, e)
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED),
                title=ft.Text("Журнал посещаемости"),
                on_click=lambda e: switch_view(attendance_view, e)
            ),
            ft.Divider(),
            ft.Container(
                content=theme_switch,
                padding=ft.padding.only(left=16)
            )
        ]
    )

    
    
    page.add(
        header_container,
        ft.Divider(),
        content_container,
    )

    # # Основной layout
    # page.add(
    #     ft.Column([
    #         content_container,
    #     ], expand=True)
    # )
    
    # Загружаем начальное представление
    switch_view(children_view)


if __name__ == "__main__":
    ft.app(target=main)

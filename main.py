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
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
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
        
        page.drawer.open = False
        page.update()

    def handle_dismissal(e):
        print(f"Drawer dismissed!")

    def handle_change(e):
        print(f"Selected Index changed: {e.control.selected_index}")
        # The actual view switching is handled by the ListTile's on_click,
        # so we just need to close the drawer here.
        page.drawer.open = False
        page.update()
    
    page.drawer = ft.NavigationDrawer(
        on_dismiss=handle_dismissal,
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
            ft.Divider(),
            ft.Container(
                content=theme_switch,
                padding=ft.padding.only(left=16)
            )
        ]
    )

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(page.drawer)),
        title=ft.Text(APP_TITLE),
        center_title=True,
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
    )
    
    # Основной layout
    page.add(
        ft.Column([
            content_container,
        ], expand=True)
    )
    
    # Загружаем начальное представление
    switch_view(children_view)


if __name__ == "__main__":
    ft.app(target=main)

"""
Главный файл приложения
"""
import flet as ft
import os
from database import KindergartenDB
from view.children_view import ChildrenView
from view.groups_view import GroupsView
from view.teachers_view import TeachersView
from view.parents_view import ParentsView
from view.attendance_view import AttendanceView
from view.settings_view import SettingsView
from view.home_view import HomeView
from navigation_drawer import AppNavigationDrawer
from settings.config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, DATABASE_NAME


def main(page: ft.Page):
    """Главная функция приложения"""
    icon_path = os.path.abspath("C:\Users\comp\Desktop\Курсовая\src\assets")
    page.window.icon = icon_path
    page.title = APP_TITLE
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.padding = 0
    
    # Загружаем сохраненную тему
    saved_theme = page.client_storage.get("app_theme")
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    # Создаем контейнер для заголовка с динамическим цветом
    header_container = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=lambda e: page.open(page.drawer),
                    key="menu_button"
                ),
                ft.Text(APP_TITLE, size=20, weight="bold", key="app_title"),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.Colors.ON_SURFACE_VARIANT,
        padding=10,
        key="header_container"
    )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        
        # Сохраняем выбранную тему
        theme_value = "dark" if page.theme_mode == ft.ThemeMode.DARK else "light"
        page.client_storage.set("app_theme", theme_value)
        
        # Обновляем цвет заголовка в зависимости от темы
        header_container.bgcolor = ft.Colors.ON_SURFACE_VARIANT
        page.update()

    theme_switch = ft.Switch(
        label="Тема приложения",
        value=page.theme_mode == ft.ThemeMode.DARK,
        on_change=toggle_theme,
        key="theme_switch"
    )
    
    # Инициализация базы данных
    db = KindergartenDB(DATABASE_NAME)
    db.connect()
    db.create_tables()
    
    # Контейнер для текущего представления
    content_container = ft.Container(expand=True, key="content_container")
    
    # Создаем представления
    home_view = HomeView(db, lambda: refresh_current_view(), page)
    children_view = ChildrenView(db, lambda: refresh_current_view(), page)
    groups_view = GroupsView(db, lambda: refresh_current_view())
    teachers_view = TeachersView(db, lambda: refresh_current_view())
    parents_view = ParentsView(db, lambda: refresh_current_view(), page)
    attendance_view = AttendanceView(db, lambda: refresh_current_view(), page)
    settings_view = SettingsView(page, theme_switch)
    
    # Текущее представление
    current_view = [home_view]
    
    def refresh_current_view():
        """Обновить текущее представление"""
        if current_view[0] == home_view:
            home_view.load_home()
        elif current_view[0] == children_view:
            children_view.load_children()
        elif current_view[0] == groups_view:
            groups_view.load_groups()
        elif current_view[0] == teachers_view:
            teachers_view.load_teachers()
        elif current_view[0] == parents_view:
            parents_view.load_parents()
        elif current_view[0] == attendance_view:
            attendance_view.load_attendance()
        elif current_view[0] == settings_view:
            settings_view.load_settings()
    
    def switch_view(view_name, e=None):
        """Переключить представление"""
        view_map = {
            "home": home_view,
            "children": children_view,
            "groups": groups_view,
            "teachers": teachers_view,
            "parents": parents_view,
            "attendance": attendance_view,
            "settings": settings_view
        }
        
        view = view_map.get(view_name)
        if not view:
            return
            
        current_view[0] = view
        content_container.content = view
        
        # Загрузить данные для представления
        if view == home_view:
            home_view.load_home()
        elif view == children_view:
            children_view.load_children()
        elif view == groups_view:
            groups_view.load_groups()
        elif view == teachers_view:
            teachers_view.load_teachers()
        elif view == parents_view:
            parents_view.load_parents()
        elif view == attendance_view:
            attendance_view.load_attendance()
        elif view == settings_view:
            settings_view.load_settings()
        
        page.drawer.open = False
        page.update()



    page.drawer = AppNavigationDrawer(switch_view)

    
    
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
    switch_view("home")


if __name__ == "__main__":
    ft.app(target=main)

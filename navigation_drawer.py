"""
Навигационное меню приложения
"""
import flet as ft
from typing import Callable


class AppNavigationDrawer(ft.NavigationDrawer):
    """Навигационное меню приложения"""
    
    def __init__(self, on_view_change: Callable):
        self.on_view_change = on_view_change
        
        super().__init__(
            on_change=self.handle_change,
            controls=[
                ft.Container(height=20, key="drawer_spacer"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HOME_OUTLINED),
                    title=ft.Text("Главная"),
                    on_click=lambda e: self.on_view_change("home", e),
                    key="nav_home"
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHILD_CARE_OUTLINED),
                    title=ft.Text("Дети"),
                    on_click=lambda e: self.on_view_change("children", e),
                    key="nav_children"
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.GROUPS_OUTLINED),
                    title=ft.Text("Группы"),
                    on_click=lambda e: self.on_view_change("groups", e),
                    key="nav_groups"
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_OUTLINED),
                    title=ft.Text("Воспитатели"),
                    on_click=lambda e: self.on_view_change("teachers", e),
                    key="nav_teachers"
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FAMILY_RESTROOM_OUTLINED),
                    title=ft.Text("Родители"),
                    on_click=lambda e: self.on_view_change("parents", e),
                    key="nav_parents"
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED),
                    title=ft.Text("Журнал посещаемости"),
                    on_click=lambda e: self.on_view_change("attendance", e),
                    key="nav_attendance"
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SETTINGS_OUTLINED),
                    title=ft.Text("Настройки"),
                    on_click=lambda e: self.on_view_change("settings", e),
                    key="nav_settings"
                )
            ]
        )
    
    def handle_change(self, e):
        """Обработчик изменения состояния drawer"""
        self.open = False
        if self.page:
            self.page.update()
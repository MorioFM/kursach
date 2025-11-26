"""
Домашняя страница приложения
"""
import flet as ft
from datetime import datetime, date
from typing import Callable
from components import InfoCard
from settings.config import PRIMARY_COLOR


class HomeView(ft.Container):
    """Домашняя страница приложения"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        
        # Приветствие
        welcome_section = ft.Container(
            content=ft.Column([
                ft.Text("Добро пожаловать!", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"Сегодня {datetime.now().strftime('%d-%m-%Y')}", size=16, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text("Система управления детским садом", size=18)
            ], spacing=5),
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            margin=ft.margin.only(bottom=20)
        )
        
        # Статистические карточки
        self.stats_row = ft.Row([], wrap=True, spacing=20)
        
        # Быстрые действия
        quick_actions = ft.Container(
            content=ft.Column([
                ft.Text("Быстрые действия", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "Добавить ребенка",
                        icon=ft.Icons.CHILD_CARE,
                        on_click=lambda e: self.navigate_to("children"),
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        )
                    ),
                    ft.ElevatedButton(
                        "Журнал посещаемости",
                        icon=ft.Icons.ASSIGNMENT,
                        on_click=lambda e: self.navigate_to("attendance"),
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        )
                    ),
                    ft.ElevatedButton(
                        "Управление группами",
                        icon=ft.Icons.GROUPS,
                        on_click=lambda e: self.navigate_to("groups"),
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        )
                    )
                ], wrap=True, spacing=10)
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            width=4200
        )
        

        
        self.content = ft.Column([
            welcome_section,
            self.stats_row,
            ft.Container(height=20),
            quick_actions
        ], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        
        # Загружаем статистику
        self.load_statistics()
    
    def load_statistics(self):
        """Загрузка статистики"""
        try:
            # Получаем статистику
            total_children = len(self.db.get_all_children())
            total_groups = len(self.db.get_all_groups())
            total_teachers = len(self.db.get_all_teachers())
            total_parents = len(self.db.get_all_parents())
            
            # Посещаемость сегодня
            today = date.today().strftime("%Y-%m-%d")
            attendance_today = 0
            for group in self.db.get_all_groups():
                if group.get('group_id'):
                    attendance_data = self.db.get_attendance_by_group_and_date(group['group_id'], today)
                    attendance_today += len([child for child in attendance_data if child.get('status') == 'Присутствует'])
            
            # Создаем карточки статистики
            cards = [
                InfoCard("Всего детей", str(total_children), ft.Icons.CHILD_CARE, "#2196F3"),
                InfoCard("Всего групп", str(total_groups), ft.Icons.GROUPS, "#4CAF50"),
                InfoCard("Всего воспитателей", str(total_teachers), ft.Icons.PERSON, "#FF9800"),
                InfoCard("Присутствуют сегодня", str(attendance_today), ft.Icons.ASSIGNMENT_TURNED_IN, "#00BCD4")
            ]
            
            self.stats_row.controls = cards
            
            if self.page:
                self.page.update()
                
        except Exception as ex:
            print(f"Ошибка при загрузке статистики: {ex}")
            import traceback
            traceback.print_exc()
    
    def navigate_to(self, view_name):
        """Навигация к другому представлению"""
        if self.page and hasattr(self.page, 'drawer'):
            # Имитируем клик по соответствующему пункту меню
            if hasattr(self.page.drawer, 'on_view_change'):
                self.page.drawer.on_view_change(view_name)
    
    def load_home(self):
        """Загрузка домашней страницы (для совместимости)"""
        self.load_statistics()
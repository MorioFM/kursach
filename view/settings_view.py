"""
Представление настроек приложения
"""
import flet as ft
from typing import Callable
from settings.config import PRIMARY_COLOR


class SettingsView(ft.Container):
    """Представление настроек приложения"""
    
    def __init__(self, page=None, theme_switch=None):
        super().__init__()
        self.page = page
        self.theme_switch = theme_switch
        
        # Секция темы
        theme_section = ft.Container(
            content=ft.Column([
                ft.Text("Внешний вид", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Тема приложения", size=16),
                        ft.Text("Переключение между светлой и темной темой", size=12, color=ft.Colors.GREY_600)
                    ], expand=True),
                    self.theme_switch if self.theme_switch else ft.Switch(label="Тема")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10
        )
        
        # Секция приложения
        app_section = ft.Container(
            content=ft.Column([
                ft.Text("О приложении", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=24),
                    ft.Column([
                        ft.Text("Система управления детским садом", size=16),
                        ft.Text("Версия 1.0.0", size=12, color=ft.Colors.GREY_600)
                    ], expand=True)
                ]),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=24),
                    ft.Column([
                        ft.Text("Функции", size=16),
                        ft.Text("Управление детьми, группами, воспитателями, родителями и журналом посещаемости", 
                               size=12, color=ft.Colors.GREY_600)
                    ], expand=True)
                ])
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10
        )
        
        self.content = ft.Column([
            ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            theme_section,
            ft.Container(height=20),
            app_section
        ], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
    
    def load_settings(self):
        """Загрузка настроек (заглушка для совместимости)"""
        pass
"""
Стили для стандартизации внешнего вида приложения
"""
import flet as ft
from settings.config import PRIMARY_COLOR


class AppStyles:
    """Класс со стилями для единообразного оформления"""
    
    # Цвета
    PRIMARY = PRIMARY_COLOR
    SUCCESS = ft.Colors.GREEN
    ERROR = ft.Colors.RED
    WARNING = ft.Colors.ORANGE
    
    # Размеры
    FIELD_WIDTH = 300
    BUTTON_HEIGHT = 40
    FORM_PADDING = 20
    FORM_SPACING = 10
    
    # Стили для заголовков
    @staticmethod
    def page_title(text: str) -> ft.Text:
        """Заголовок страницы"""
        return ft.Text(text, size=24, weight=ft.FontWeight.BOLD)
    
    @staticmethod
    def form_title(text: str) -> ft.Text:
        """Заголовок формы"""
        return ft.Text(text, size=20, weight=ft.FontWeight.BOLD)
    
    @staticmethod
    def section_title(text: str) -> ft.Text:
        """Заголовок секции"""
        return ft.Text(text, size=18, weight=ft.FontWeight.BOLD)
    
    # Стили для полей ввода
    @staticmethod
    def text_field(label: str, required: bool = False, **kwargs) -> ft.TextField:
        """Стандартное текстовое поле"""
        return ft.TextField(
            label=f"{label}{'*' if required else ''}",
            width=AppStyles.FIELD_WIDTH,
            **kwargs
        )
    
    @staticmethod
    def dropdown_field(label: str, options: list, required: bool = False, **kwargs) -> ft.Dropdown:
        """Стандартный выпадающий список"""
        return ft.Dropdown(
            label=f"{label}{'*' if required else ''}",
            width=AppStyles.FIELD_WIDTH,
            options=options,
            **kwargs
        )
    
    @staticmethod
    def error_text(text: str = "") -> ft.Text:
        """Текст ошибки"""
        return ft.Text(text, color=ft.Colors.ERROR, size=12, visible=False)
    
    # Стили для кнопок
    @staticmethod
    def primary_button(text: str, icon=None, **kwargs) -> ft.ElevatedButton:
        """Основная кнопка"""
        return ft.ElevatedButton(
            text,
            icon=icon,
            bgcolor=AppStyles.PRIMARY,
            color=ft.Colors.WHITE,
            height=AppStyles.BUTTON_HEIGHT,
            **kwargs
        )
    
    @staticmethod
    def secondary_button(text: str, icon=None, **kwargs) -> ft.OutlinedButton:
        """Вторичная кнопка"""
        return ft.OutlinedButton(
            text,
            icon=icon,
            height=AppStyles.BUTTON_HEIGHT,
            **kwargs
        )
    
    @staticmethod
    def icon_button(icon, tooltip: str, **kwargs) -> ft.IconButton:
        """Кнопка с иконкой"""
        return ft.IconButton(
            icon=icon,
            tooltip=tooltip,
            **kwargs
        )
    
    # Стили для контейнеров
    @staticmethod
    def form_container(content, visible: bool = False) -> ft.Container:
        """Контейнер формы"""
        return ft.Container(
            content=content,
            padding=AppStyles.FORM_PADDING,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            visible=visible
        )
    
    @staticmethod
    def card_container(content, **kwargs) -> ft.Container:
        """Контейнер-карточка"""
        return ft.Container(
            content=content,
            padding=15,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            **kwargs
        )
    
    # Стили для строк и колонок
    @staticmethod
    def form_row(controls: list, spacing: int = None) -> ft.Row:
        """Строка в форме"""
        return ft.Row(
            controls,
            spacing=spacing or AppStyles.FORM_SPACING
        )
    
    @staticmethod
    def form_column(controls: list, spacing: int = None) -> ft.Column:
        """Колонка в форме"""
        return ft.Column(
            controls,
            spacing=spacing or AppStyles.FORM_SPACING
        )
    
    @staticmethod
    def page_header(title: str, add_button_text: str = None, on_add_click=None) -> ft.Row:
        """Заголовок страницы с кнопкой добавления"""
        controls = [AppStyles.page_title(title)]
        
        if add_button_text and on_add_click:
            controls.append(
                AppStyles.primary_button(
                    add_button_text,
                    icon=ft.Icons.ADD,
                    on_click=on_add_click
                )
            )
        
        return ft.Row(
            controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    @staticmethod
    def button_row(buttons: list) -> ft.Row:
        """Строка с кнопками"""
        return ft.Row(buttons, spacing=AppStyles.FORM_SPACING)
"""
Переиспользуемые UI компоненты
"""
import flet as ft
from typing import Callable, Optional


class ConfirmDialog(ft.AlertDialog):
    """Диалог подтверждения действия"""
    def __init__(self, title: str, content: str, on_confirm: Callable):
        super().__init__(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close()),
                ft.TextButton(
                    "Подтвердить",
                    on_click=lambda e: self.confirm_and_close(on_confirm)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
    
    def close(self):
        self.open = False
        self.page.update()
    
    def confirm_and_close(self, on_confirm: Callable):
        on_confirm(True)  # Передаем True как параметр confirmed
        self.close()
        if self.page:
            self.page.update()


class InfoCard(ft.Container):
    """Информационная карточка"""
    def __init__(self, title: str, value: str, icon: str, color: str = "#2196F3"):
        super().__init__(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=14, color=ft.Colors.GREY_700),
                ]),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ], spacing=5),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )


class DataTable(ft.Container):
    """Таблица данных с возможностью редактирования и удаления"""
    def __init__(self, columns: list, rows: list, on_edit: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None):
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Создаем колонки таблицы
        table_columns = [ft.DataColumn(ft.Text(col)) for col in columns]
        
        # Добавляем колонку действий если есть обработчики
        if on_edit or on_delete:
            table_columns.append(ft.DataColumn(ft.Text("Действия")))
        
        self.table = ft.DataTable(
            columns=table_columns,
            rows=[], # Initialize with empty rows, will be set by set_rows
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
        )
        
        super().__init__(
            content=self.table,
            padding=10,
        )
        self.set_rows(rows) # Call set_rows to populate initial data
    
    def set_rows(self, rows_data: list):
        """
        Устанавливает строки таблицы.
        Принимает данные в формате: [{"id": 1, "values": ["a", "b"]}, ...]
        """
        self.table.rows.clear()
        for row_item in rows_data:
            # Убедимся, что элемент - это словарь
            if not isinstance(row_item, dict):
                continue

            row_id = row_item.get('id')
            row_values = row_item.get('values', [])

            if row_id is None:
                continue

            cells = [ft.DataCell(ft.Text(str(value))) for value in row_values]
            
            # Добавляем кнопки управления, если есть обработчики
            if self.on_edit or self.on_delete:
                action_buttons = []
                if self.on_edit:
                    action_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=ft.Colors.BLUE,
                            tooltip="Редактировать",
                            on_click=lambda e, rid=row_id: self.on_edit(rid)
                        )
                    )
                if self.on_delete:
                    action_buttons.append(
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED,
                            tooltip="Удалить",
                            on_click=lambda e, rid=row_id: self.on_delete(rid)
                        )
                    )
                cells.append(ft.DataCell(ft.Row(action_buttons)))
            
            self.table.rows.append(ft.DataRow(cells=cells))
        
        if self.page:
            self.update()


class SearchBar(ft.Container):
    """Строка поиска"""
    def __init__(self, on_search: Callable, placeholder: str = "Поиск..."):
        self.search_field = ft.TextField(
            hint_text=placeholder,
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: on_search(e.control.value),
            expand=True,
        )
        
        super().__init__(
            content=self.search_field,
            padding=10,
        )

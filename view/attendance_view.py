"""
Представление для управления журналом посещаемости
"""
import flet as ft
from datetime import datetime, date
from typing import Callable
from settings.config import PRIMARY_COLOR


class AttendanceView(ft.Container):
    """Представление для управления журналом посещаемости"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        self.selected_date = date.today().strftime("%Y-%m-%d")
        self.selected_group_id = None
        
        # Выбор группы
        groups = self.db.get_all_groups()
        self.group_dropdown = ft.Dropdown(
            label="Выберите группу",
            width=300,
            options=[
                ft.DropdownOption(str(g['group_id']), g['group_name']) 
                for g in groups if g['group_id']
            ],
            on_change=self.on_group_change
        )
        
        # Выбор даты
        self.date_picker = ft.DatePicker(
            on_change=self.on_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            help_text="Выберите дату",
            cancel_text="Отмена",
            confirm_text="ОК",
            error_format_text="Неверный формат даты",
            error_invalid_text="Неверная дата",
            field_hint_text="дд/мм/гггг",
            field_label_text="Дата"
        )
        
        display_date = datetime.strptime(self.selected_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        self.date_button = ft.ElevatedButton(
            f"Дата: {display_date}",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=self.open_date_picker
        )
        
        # Контейнер для таблицы посещаемости
        self.attendance_container = ft.Container(
            content=ft.Text("Выберите группу для просмотра журнала", size=16),
            expand=True
        )
        
        self.content = ft.Column([
            ft.Text("Журнал посещаемости", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.group_dropdown,
                self.date_button
            ], spacing=20),
            self.attendance_container
        ], spacing=20, expand=True)
        
        self.page.overlay.append(self.date_picker)
    
    def on_group_change(self, e):
        """Обработчик изменения группы"""
        self.selected_group_id = int(e.control.value) if e.control.value else None
        self.load_attendance()
    
    def open_date_picker(self, e):
        """Открыть выбор даты"""
        self.date_picker.open = True
        self.page.update()
    
    def on_date_change(self, e):
        """Обработчик изменения даты"""
        if e.control.value:
            # Сохраняем в формате YYYY-MM-DD для базы данных
            self.selected_date = e.control.value.strftime("%Y-%m-%d")
            # Отображаем в формате DD-MM-YYYY
            display_date = e.control.value.strftime("%d-%m-%Y")
            self.date_button.text = f"Дата: {display_date}"
            self.date_button.update()
            self.load_attendance()
    
    def load_attendance(self):
        """Загрузка данных посещаемости"""
        if not self.selected_group_id:
            return
        
        children_data = self.db.get_attendance_by_group_and_date(
            self.selected_group_id, 
            self.selected_date
        )
        
        if not children_data:
            self.attendance_container.content = ft.Text(
                "В выбранной группе нет детей", 
                size=16
            )
            if self.page:
                self.page.update()
            return
        
        # Создаем таблицу с редактируемыми ячейками
        rows = []
        for child in children_data:
            status_dropdown = ft.Dropdown(
                value=child['status'],
                width=200,
                options=[
                    ft.DropdownOption("Присутствует", "Присутствует"),
                    ft.DropdownOption("Отсутствует", "Отсутствует"),
                    ft.DropdownOption("Болеет", "Болеет")
                ],
                on_change=lambda e, child_id=child['child_id']: self.update_status(child_id, e.control.value, '')
            )
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{child['last_name']} {child['first_name']}")),
                        ft.DataCell(status_dropdown)
                    ]
                )
            )
        
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ребенок")),
                ft.DataColumn(ft.Text("Статус"))
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.OUTLINE_VARIANT
        )
        
        # Преобразуем дату для отображения
        display_date = datetime.strptime(self.selected_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        self.attendance_container.content = ft.Column([
            ft.Text(f"Посещаемость на {display_date}", size=18, weight=ft.FontWeight.BOLD),
            attendance_table
        ], scroll=ft.ScrollMode.AUTO)
        
        if self.page:
            self.page.update()
    
    def update_status(self, child_id: int, status: str, notes: str = ''):
        """Обновление статуса посещаемости в реальном времени"""
        try:
            self.db.update_attendance_record(child_id, self.selected_date, status, notes)
        except Exception as ex:
            self.show_error(f"Ошибка при обновлении статуса: {str(ex)}")
    

    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
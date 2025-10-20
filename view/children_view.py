"""
Представление для управления детьми
"""
import flet as ft
from datetime import datetime
from typing import Callable
from settings.models import format_date
from datetime import date # Import date for age calculation
from components import ConfirmDialog, DataTable, SearchBar
from dialogs import show_confirm_dialog
from settings.config import GENDERS


class ChildrenView(ft.Container):
    """Представление для управления детьми"""
    
    def __init__(self, db, on_refresh: Callable = None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.selected_child = None
        self.search_query = ""
        
        # Поля формы
        self.last_name_field = ft.TextField(
            label="Фамилия",
            width=300,
            autofocus=True
        )
        self.first_name_field = ft.TextField(
            label="Имя",
            width=300
        )
        self.middle_name_field = ft.TextField(
            label="Отчество",
            width=300
        )
        self.birth_date_field = ft.TextField(
            label="Дата рождения (ГГГГ-ММ-ДД)",
            width=300,
            hint_text="2020-01-15"
        )
        self.gender_dropdown = ft.Dropdown(
            label="Пол",
            width=300,
            options=[ft.DropdownOption(k, v) for k, v in GENDERS.items()]
        )
        
        # Получаем список групп для dropdown
        groups = self.db.get_all_groups()
        self.group_dropdown = ft.Dropdown(
            label="Группа",
            width=300,
            options=[
                ft.DropdownOption(str(g['group_id']), g['group_name']) 
                for g in groups
            ]
        )
        
        self.enrollment_date_field = ft.TextField(
            label="Дата зачисления (ГГГГ-ММ-ДД)",
            width=300,
            hint_text="2024-09-01",
            value=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Кнопки формы
        self.save_button = ft.ElevatedButton(
            "Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self.save_child
        )
        self.cancel_button = ft.OutlinedButton(
            "Отмена",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_edit
        )
        
        # Форма
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Добавить ребенка", size=20, weight=ft.FontWeight.BOLD),
                self.last_name_field,
                self.first_name_field,
                self.middle_name_field,
                self.birth_date_field,
                self.gender_dropdown,
                self.group_dropdown,
                self.enrollment_date_field,
                ft.Row([
                    self.save_button,
                    self.cancel_button
                ], spacing=10)
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            visible=False
        )
        
        # Поиск
        self.search_bar = SearchBar(on_search=self.on_search)
        
        # Таблица
        self.data_table = DataTable(
            columns=[
                "№", "Фамилия", "Имя", "Отчество", "Дата рождения", 
                "Возраст", "Пол", "Группа", "Дата зачисления"
            ],
            rows=[],
            on_edit=self.edit_child,
            on_delete=self.delete_child
        )
        
        # Кнопка добавления
        add_button = ft.ElevatedButton(
            "Добавить ребенка",
            icon=ft.Icons.ADD,
            on_click=self.show_add_form
        )
        
        # Загружаем данные
        self.load_children()
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("Дети", size=24, weight=ft.FontWeight.BOLD),
                add_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.form_container,
            self.search_bar,
            self.data_table
        ], spacing=20, expand=True)
    
    def load_children(self, search_query: str = ""):
        """Загрузка списка детей"""
        if search_query:
            children = self.db.search_children(search_query)
        else:
            children = self.db.get_all_children()
        
        rows = []
        for i, child in enumerate(children, 1):
            birth_date_obj = datetime.strptime(child['birth_date'], "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
            
            # Формируем данные в новом формате: {"id": ..., "values": [...]}
            rows.append({
                "id": child['child_id'],
                "values": [
                    str(i), # Порядковый номер
                    child['last_name'],
                    child['first_name'],
                    child['middle_name'] or '',
                    format_date(child['birth_date']),
                    str(age),
                    GENDERS.get(child['gender'], child['gender']),
                    child.get('group_name', 'Не назначена'),
                    format_date(child['enrollment_date'])
                ]
            })
        
        self.data_table.set_rows(rows)
        if self.page:
            self.update()
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_child = None
        self.clear_form()
        self.form_container.content.controls[0].value = "Добавить ребенка"
        self.form_container.visible = True
        self.update()
    
    def edit_child(self, child_id: str):
        """Редактировать ребенка"""
        child = self.db.get_child_by_id(int(child_id))
        if child:
            self.selected_child = child
            self.last_name_field.value = child['last_name']
            self.first_name_field.value = child['first_name']
            self.middle_name_field.value = child['middle_name'] or ''
            self.birth_date_field.value = child['birth_date']
            self.gender_dropdown.value = child['gender']
            self.group_dropdown.value = str(child['group_id']) if child['group_id'] else None
            self.enrollment_date_field.value = child['enrollment_date']
            
            self.form_container.content.controls[0].value = "Редактировать ребенка"
            self.form_container.visible = True
            self.update()
    
    def delete_child(self, child_id: str):
        """Удалить ребенка"""
        def on_yes(e):
            try:
                self.db.delete_child(int(child_id))
                self.load_children(self.search_query)
                if self.on_refresh:
                    self.on_refresh()
            except Exception as ex:
                self.show_error(f"Ошибка при удалении: {str(ex)}")

        show_confirm_dialog(
            self.page,
            title="Удаление ребенка",
            content="Вы уверены, что хотите удалить этого ребенка?",
            on_yes=on_yes,
            adaptive=True,
        )
    
    def save_child(self, e):
        """Сохранить ребенка"""
        # Валидация
        if not all([
            self.last_name_field.value,
            self.first_name_field.value,
            self.birth_date_field.value,
            self.gender_dropdown.value,
            self.enrollment_date_field.value
        ]):
            self.show_error("Пожалуйста, заполните все обязательные поля")
            return
        
        try:
            child_data = {
                'last_name': self.last_name_field.value,
                'first_name': self.first_name_field.value,
                'middle_name': self.middle_name_field.value or None,
                'birth_date': self.birth_date_field.value,
                'gender': self.gender_dropdown.value,
                'group_id': int(self.group_dropdown.value) if self.group_dropdown.value else None,
                'enrollment_date': self.enrollment_date_field.value
            }
            
            if self.selected_child:
                # Обновление
                self.db.update_child(self.selected_child['child_id'], **child_data)
            else:
                # Добавление
                self.db.add_child(
                    last_name=child_data['last_name'],
                    first_name=child_data['first_name'],
                    middle_name=child_data['middle_name'],
                    birth_date=child_data['birth_date'],
                    gender=child_data['gender'],
                    group_id=child_data['group_id'],
                    enrollment_date=child_data['enrollment_date']
                )
            
            self.form_container.visible = False
            self.load_children(self.search_query)
            if self.on_refresh:
                self.on_refresh()
            self.update()
            
        except Exception as ex:
            self.show_error(f"Ошибка при сохранении: {str(ex)}")
    
    def cancel_edit(self, e):
        """Отменить редактирование"""
        self.form_container.visible = False
        self.clear_form()
        self.update()
    
    def clear_form(self):
        """Очистить форму"""
        self.last_name_field.value = ""
        self.first_name_field.value = ""
        self.middle_name_field.value = ""
        self.birth_date_field.value = ""
        self.gender_dropdown.value = None
        self.group_dropdown.value = None
        self.enrollment_date_field.value = datetime.now().strftime("%Y-%m-%d")
    
    def on_search(self, query: str):
        """Обработка поиска"""
        self.search_query = query
        self.load_children(query)
    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def refresh(self):
        """Обновить данные"""
        # Обновляем список групп в dropdown
        groups = self.db.get_all_groups()
        self.group_dropdown.options = [
            ft.DropdownOption(str(g['group_id']), g['group_name']) 
            for g in groups
        ]
        self.load_children(self.search_query)

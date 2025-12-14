"""
Представление для управления детьми
"""
import flet as ft
from datetime import datetime
from typing import Callable
from settings.models import format_date
from datetime import date # Import date for age calculation
from components import ConfirmDialog, SearchBar
from dialogs import show_confirm_dialog
from settings.config import GENDERS
from pages_styles.styles import AppStyles


class ChildrenView(ft.Container):
    """Представление для управления детьми"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.selected_child = None
        self.search_query = ""
        self.page = page
        
        # Поля формы
        self.last_name_field = AppStyles.text_field("Фамилия", required=True, autofocus=True)
        self.last_name_error = AppStyles.error_text()
        
        self.first_name_field = AppStyles.text_field("Имя", required=True)
        self.first_name_error = AppStyles.error_text()
        
        self.middle_name_field = AppStyles.text_field("Отчество")
        
        self.birth_date_field = AppStyles.text_field("Дата рождения", required=True, hint_text="дд-мм-гггг", max_length=10, on_change=self.format_birth_date)
        self.birth_date_error = AppStyles.error_text()
        
        self.gender_dropdown = AppStyles.dropdown_field("Пол", [ft.DropdownOption(k, v) for k, v in GENDERS.items()], required=True)
        self.gender_error = AppStyles.error_text()
        
        # Получаем список групп для dropdown
        groups = self.db.get_all_groups()
        self.group_dropdown = ft.Dropdown(
            label="Группа",
            width=300,
            options=[
                ft.DropdownOption("0", "Без группы")
            ] + [
                ft.DropdownOption(str(g['group_id']), g['group_name']) 
                for g in groups
            ]
        )
        
        self.enrollment_date_field = AppStyles.text_field("Дата зачисления", required=True, hint_text="дд-мм-гггг", max_length=10, value=datetime.now().strftime("%d-%m-%Y"), on_change=self.format_enrollment_date)
        self.enrollment_date_error = AppStyles.error_text()
        
        # Кнопки формы
        self.save_button = AppStyles.primary_button("Сохранить", icon=ft.Icons.SAVE, on_click=self.save_child)
        self.cancel_button = AppStyles.secondary_button("Отмена", icon=ft.Icons.CANCEL, on_click=self.cancel_edit)
        
        # Форма
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Добавить ребенка", size=20, weight=ft.FontWeight.BOLD),
                self.last_name_field,
                self.last_name_error,
                self.first_name_field,
                self.first_name_error,
                self.middle_name_field,
                self.birth_date_field,
                self.birth_date_error,
                self.gender_dropdown,
                self.gender_error,
                self.group_dropdown,
                self.enrollment_date_field,
                self.enrollment_date_error,
                ft.Row([
                    self.save_button,
                    self.cancel_button
                ], spacing=10)
            ], spacing=5),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            visible=False,
        )
        
        # Поиск
        self.search_bar = SearchBar(on_search=self.on_search)
        
        # Список детей
        self.children_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        # Кнопка добавления
        add_button = AppStyles.primary_button("Добавить ребенка", icon=ft.Icons.ADD, on_click=self.show_add_form)
        
        # Загружаем данные
        self.load_children()
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Дети", "Добавить ребенка", self.show_add_form),
            self.form_container,
            self.search_bar,
            ft.Container(content=self.children_list, expand=True)
        ], spacing=20)
        self.expand = True
    
    def load_children(self, search_query: str = ""):
        """Загрузка списка детей"""
        children = self.db.search_children(search_query) if search_query else self.db.get_all_children()
        self.children_list.controls = [self._create_child_item(child) for child in children]
        if self.page:
            self.page.update()
    
    def _create_child_item(self, child):
        """Создать элемент списка для ребенка"""
        birth_date_str = child['birth_date']
        try:
            if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            else:
                birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
        except ValueError:
            birth_date_obj = date.today()
        
        today = date.today()
        age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        
        return ft.ListTile(
            title=ft.Text(f"{child['last_name']} {child['first_name']} {child['middle_name'] or ''}", weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"ДР: {format_date(child['birth_date'])} | {age} лет | {GENDERS.get(child['gender'], child['gender'])} | {child.get('group_name') if child.get('group_id') else 'Без группы'}"),
            trailing=ft.PopupMenuButton(
                tooltip="",
                items=[
                    ft.PopupMenuItem(text="Родители", icon=ft.Icons.FAMILY_RESTROOM, on_click=lambda _, cid=child['child_id']: self.manage_parents(str(cid))),
                    ft.PopupMenuItem(text="Редактировать", icon=ft.Icons.EDIT, on_click=lambda _, cid=child['child_id']: self.edit_child(str(cid))),
                    ft.PopupMenuItem(text="Удалить", icon=ft.Icons.DELETE, on_click=lambda _, cid=child['child_id']: self.delete_child(str(cid)))
                ]
            )
        )
    
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
            self.group_dropdown.value = str(child['group_id']) if child['group_id'] else "0"
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
    
    def clear_field_errors(self):
        """Очистить все сообщения об ошибках"""
        self.last_name_error.visible = False
        self.first_name_error.visible = False
        self.birth_date_error.visible = False
        self.gender_error.visible = False
        self.enrollment_date_error.visible = False
    
    def validate_fields(self):
        """Проверить обязательные поля и показать ошибки"""
        self.clear_field_errors()
        is_valid = True
        
        if not self.last_name_field.value or not self.last_name_field.value.strip():
            self.last_name_error.value = "Заполните поле"
            self.last_name_error.visible = True
            is_valid = False
        
        if not self.first_name_field.value or not self.first_name_field.value.strip():
            self.first_name_error.value = "Заполните поле"
            self.first_name_error.visible = True
            is_valid = False
        
        if not self.birth_date_field.value or not self.birth_date_field.value.strip():
            self.birth_date_error.value = "Заполните поле"
            self.birth_date_error.visible = True
            is_valid = False
        
        if not self.gender_dropdown.value:
            self.gender_error.value = "Заполните поле"
            self.gender_error.visible = True
            is_valid = False
        
        if not self.enrollment_date_field.value or not self.enrollment_date_field.value.strip():
            self.enrollment_date_error.value = "Заполните поле"
            self.enrollment_date_error.visible = True
            is_valid = False
        
        if not is_valid:
            self.update()
        
        return is_valid
    
    def save_child(self, e):
        """Сохранить ребенка"""
        # Проверка обязательных полей
        if not self.validate_fields():
            return
        
        try:
            child_data = {
                'last_name': self.last_name_field.value,
                'first_name': self.first_name_field.value,
                'middle_name': self.middle_name_field.value or None,
                'birth_date': self.birth_date_field.value,
                'gender': self.gender_dropdown.value,
                'group_id': int(self.group_dropdown.value) if self.group_dropdown.value and self.group_dropdown.value != "0" else None,
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
        self.group_dropdown.value = "0"
        self.enrollment_date_field.value = datetime.now().strftime("%Y-%m-%d")
        self.clear_field_errors()
    
    def on_search(self, query: str):
        """Обработка поиска"""
        self.search_query = query
        self.load_children(query)
    
    def manage_parents(self, child_id: str):
        """Управление родителями ребенка"""
        try:
            child = self.db.get_child_by_id(int(child_id))
            if not child:
                return
            
            # Получаем список всех родителей и текущих связей
            all_parents = self.db.get_all_parents()
            current_parents = self.db.get_parents_by_child(int(child_id))
            current_parent_ids = [p['parent_id'] for p in current_parents]
            
            # Создаем диалог
            parent_checkboxes = []
            relationship_fields = {}
            parent_rows = []
            
            for parent in all_parents:
                is_selected = parent['parent_id'] in current_parent_ids
                current_relationship = ""
                if is_selected:
                    current_rel = next((p for p in current_parents if p['parent_id'] == parent['parent_id']), None)
                    if current_rel:
                        current_relationship = current_rel['relationship']
                
                checkbox = ft.Checkbox(
                    label=f"{parent.get('last_name', '')} {parent.get('first_name', '')}",
                    value=is_selected,
                    data=parent['parent_id']
                )
                
                relationship_field = ft.TextField(
                    label="Степень родства",
                    value=current_relationship,
                    width=150,
                    hint_text="Мама, Папа..."
                )
                
                parent_checkboxes.append(checkbox)
                relationship_fields[parent['parent_id']] = relationship_field
                parent_rows.append(ft.Row([checkbox, relationship_field], spacing=10))
            
            def save_relations(e):
                try:
                    # Удаляем все старые связи
                    for parent_id in current_parent_ids:
                        self.db.remove_parent_child_relation(parent_id, int(child_id))
                    
                    # Добавляем новые связи
                    for checkbox in parent_checkboxes:
                        if checkbox.value:
                            parent_id = checkbox.data
                            relationship = relationship_fields[parent_id].value or "Родитель"
                            self.db.add_parent_child_relation(parent_id, int(child_id), relationship)
                    
                    self.page.close(dialog)
                    
                except Exception as ex:
                    self.show_error(f"Ошибка при сохранении: {str(ex)}")
            
            def close_dialog(e):
                self.page.close(dialog)
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Родители: {child['last_name']} {child['first_name']}"),
                content=ft.Container(
                    content=ft.Column(parent_rows, scroll=ft.ScrollMode.AUTO),
                    width=400,
                    height=300
                ),
                actions=[
                    ft.TextButton("Отмена", on_click=close_dialog),
                    ft.ElevatedButton("Сохранить", on_click=save_relations)
                ]
            )
            
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as ex:
            self.show_error(f"Ошибка: {str(ex)}")
    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    

    def format_birth_date(self, e):
        """Форматирование даты рождения в формате дд-мм-гггг"""
        value = e.control.value
        digits = ''.join(filter(str.isdigit, value))
        
        if len(digits) > 8:
            digits = digits[:8]
        
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"
        
        e.control.value = formatted
        e.control.update()
    
    def format_enrollment_date(self, e):
        """Форматирование даты зачисления в формате дд-мм-гггг"""
        value = e.control.value
        digits = ''.join(filter(str.isdigit, value))
        
        if len(digits) > 8:
            digits = digits[:8]
        
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"
        
        e.control.value = formatted
        e.control.update()
    
    def refresh(self):
        """Обновить данные"""
        # Обновляем список групп в dropdown
        groups = self.db.get_all_groups()
        self.group_dropdown.options = [
            ft.DropdownOption("0", "Без группы")
        ] + [
            ft.DropdownOption(str(g['group_id']), g['group_name']) 
            for g in groups
        ]
        self.load_children(self.search_query)

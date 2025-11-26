"""
Представление для управления родителями
"""
import flet as ft
from typing import Callable
from components import DataTable, SearchBar
from dialogs import show_confirm_dialog
from settings.config import PRIMARY_COLOR
from pages_styles.styles import AppStyles


class ParentsView(ft.Container):
    """Представление для управления родителями"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.selected_parent = None
        self.page = page
        self.search_query = ""
        
        # Поля формы
        self.last_name_field = AppStyles.text_field("Фамилия", required=True, autofocus=True)
        self.last_name_error = AppStyles.error_text()
        
        self.first_name_field = AppStyles.text_field("Имя", required=True)
        self.first_name_error = AppStyles.error_text()
        self.middle_name_field = ft.TextField(
            label="Отчество",
            width=300
        )
        # Код страны
        self.country_code_dropdown = ft.Dropdown(
            label="Код страны",
            width=150,
            value="+7",
            options=[
                ft.DropdownOption("+7", "+7 (Россия)"),
                ft.DropdownOption("+375", "+375 (Беларусь)"),
                ft.DropdownOption("+1", "+1 (США)"),
                ft.DropdownOption("+380", "+380 (Украина)"),
                ft.DropdownOption("+49", "+49 (Германия)")
            ],
            on_change=self.update_phone_hint
        )
        
        self.phone_field = ft.TextField(
            label="Номер телефона",
            width=140,
            keyboard_type=ft.KeyboardType.PHONE,
            hint_text="000-000-00-00",
            max_length=15,
            on_change=self.format_phone
        )
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            keyboard_type=ft.KeyboardType.EMAIL
        )
        self.address_field = ft.TextField(
            label="Адрес проживания",
            width=300,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        
        # Кнопки формы
        self.save_button = ft.ElevatedButton(
            "Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self.save_parent,
            bgcolor=PRIMARY_COLOR,
            color=ft.Colors.WHITE
        )
        self.cancel_button = ft.OutlinedButton(
            "Отмена",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_edit
        )
        
        # Форма
        self.form_title = ft.Text("Добавить родителя", size=20, weight=ft.FontWeight.BOLD)
        self.form_container = ft.Container(
            content=ft.Column([
                self.form_title,
                self.last_name_field,
                self.last_name_error,
                self.first_name_field,
                self.first_name_error,
                self.middle_name_field,
                ft.Row([
                    self.country_code_dropdown,
                    self.phone_field
                ], spacing=10),
                self.email_field,
                self.address_field,
                ft.Row([
                    self.save_button,
                    self.cancel_button
                ], spacing=10)
            ], spacing=5),
            padding=20,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            visible=False
        )
        
        # Поиск
        self.search_bar = SearchBar(on_search=self.on_search, placeholder="Поиск родителей...")
        
        # Таблица
        self.data_table = DataTable(
            columns=["№", "ФИО", "Телефон", "Email", "Адрес"],
            rows=[],
            on_edit=self.edit_parent,
            on_delete=self.delete_parent
        )
        
        # Кнопка добавления
        add_button = AppStyles.primary_button("Добавить родителя", icon=ft.Icons.ADD, on_click=self.show_add_form)
        
        # Загружаем данные
        self.load_parents()
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Родители", "Добавить родителя", self.show_add_form),
            self.form_container,
            self.search_bar,
            self.data_table
        ], spacing=20)
        self.expand = True
    
    def on_search(self, query: str):
        """Обработчик поиска"""
        self.search_query = query
        self.load_parents(query)
    
    def load_parents(self, search_query: str = ""):
        """Загрузка списка родителей"""
        if search_query:
            parents = self.db.search_parents(search_query)
        else:
            parents = self.db.get_all_parents()
        
        rows = []
        for i, parent in enumerate(parents, 1):
            rows.append({
                "id": parent['parent_id'],
                "values": [
                    str(i),
                    parent.get('full_name', ''),
                    parent.get('phone', ''),
                    parent.get('email', ''),
                    parent.get('address', '')
                ]
            })
        
        self.data_table.set_rows(rows)
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_parent = None
        self.clear_form()
        self.form_title.value = "Добавить родителя"
        self.form_container.visible = True
        self.update()
    
    def edit_parent(self, parent_id: str):
        """Редактировать родителя"""
        parent = self.db.get_parent_by_id(int(parent_id))
        if parent:
            self.selected_parent = parent
            self.last_name_field.value = parent['last_name']
            self.first_name_field.value = parent['first_name']
            self.middle_name_field.value = parent['middle_name'] or ''
            
            # Разбираем телефон на код страны и номер
            phone = parent['phone'] or ''
            if phone.startswith('+375'):
                self.country_code_dropdown.value = '+375'
                self.phone_field.value = phone[4:]
            elif phone.startswith('+1'):
                self.country_code_dropdown.value = '+1'
                self.phone_field.value = phone[2:]
            elif phone.startswith('+7'):
                self.country_code_dropdown.value = '+7'
                self.phone_field.value = phone[2:]
            else:
                self.country_code_dropdown.value = '+7'
                self.phone_field.value = phone
            
            self.email_field.value = parent['email'] or ''
            self.address_field.value = parent['address'] or ''
            
            self.form_title.value = "Редактировать родителя"
            self.form_container.visible = True
            self.update()
    
    def delete_parent(self, parent_id: str):
        """Удалить родителя"""
        parent = self.db.get_parent_by_id(int(parent_id))
        if not parent:
            self.show_error("Родитель не найден")
            return

        def on_yes(e):
            try:
                self.db.delete_parent(int(parent_id))
                self.load_parents(self.search_query)
                if self.on_refresh:
                    self.on_refresh()
                self.show_success(f"Родитель {parent['full_name']} успешно удален")
            except Exception as ex:
                self.show_error(f"Ошибка при удалении родителя: {str(ex)}")

        show_confirm_dialog(
            self.page,
            title="Удаление родителя",
            content=f"Вы уверены, что хотите удалить родителя {parent['full_name']}?",
            on_yes=on_yes,
            adaptive=True
        )
    
    def update_phone_hint(self, e):
        """Обновить подсказку для телефона в зависимости от кода страны"""
        code = e.control.value
        if code == "+7":
            self.phone_field.hint_text = "000-000-00-00"
        elif code == "+375":
            self.phone_field.hint_text = "00-000-00-00"
        elif code == "+1":
            self.phone_field.hint_text = "000-000-0000"
        else:
            self.phone_field.hint_text = "000-000-00-00"
        self.phone_field.update()
    
    def format_phone(self, e):
        """Форматирование номера телефона"""
        value = e.control.value
        digits = ''.join(filter(str.isdigit, value))
        
        # Ограничиваем до 10 цифр (без кода страны)
        if len(digits) > 10:
            digits = digits[:10]
        
        # Применяем маску в зависимости от кода страны
        code = self.country_code_dropdown.value
        
        if code == "+1":  # США
            if len(digits) <= 3:
                formatted = digits
            elif len(digits) <= 6:
                formatted = f"{digits[:3]}-{digits[3:]}"
            else:
                formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif code == "+375":  # Беларусь
            if len(digits) <= 2:
                formatted = digits
            elif len(digits) <= 5:
                formatted = f"{digits[:2]}-{digits[2:]}"
            elif len(digits) <= 7:
                formatted = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
            else:
                formatted = f"{digits[:2]}-{digits[2:5]}-{digits[5:7]}-{digits[7:]}"
        else:  # Россия и другие
            if len(digits) <= 3:
                formatted = digits
            elif len(digits) <= 6:
                formatted = f"{digits[:3]}-{digits[3:]}"
            elif len(digits) <= 8:
                formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            else:
                formatted = f"{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
        
        e.control.value = formatted
        e.control.update()
    
    def clear_field_errors(self):
        """Очистить все сообщения об ошибках"""
        self.last_name_error.visible = False
        self.first_name_error.visible = False
    
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
        
        if not is_valid:
            self.update()
        
        return is_valid
    
    def save_parent(self, e):
        """Сохранить родителя"""
        # Проверка обязательных полей
        if not self.validate_fields():
            return
        
        try:
            if self.selected_parent:
                # Обновление
                # Собираем полный номер телефона
                full_phone = None
                if self.phone_field.value and self.phone_field.value.strip():
                    full_phone = self.country_code_dropdown.value + self.phone_field.value.replace('-', '')
                
                self.db.update_parent(
                    self.selected_parent['parent_id'],
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=full_phone,
                    email=self.email_field.value or None,
                    address=self.address_field.value or None
                )
                self.show_success("Родитель успешно обновлен")
            else:
                # Добавление
                # Собираем полный номер телефона
                full_phone = None
                if self.phone_field.value and self.phone_field.value.strip():
                    full_phone = self.country_code_dropdown.value + self.phone_field.value.replace('-', '')
                
                self.db.add_parent(
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=full_phone,
                    email=self.email_field.value or None,
                    address=self.address_field.value or None
                )
                self.show_success("Родитель успешно добавлен")
            
            self.form_container.visible = False
            self.load_parents(self.search_query)
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
        self.country_code_dropdown.value = "+7"
        self.phone_field.value = ""
        self.email_field.value = ""
        self.address_field.value = ""
        self.clear_field_errors()
    
    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_success(self, message: str):
        """Показать успешное сообщение"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
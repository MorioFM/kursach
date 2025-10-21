"""
Представление для управления воспитателями
"""
import flet as ft
from typing import Callable
from components import DataTable, SearchBar
from dialogs import show_confirm_dialog
from settings.config import PRIMARY_COLOR


class TeachersView(ft.Container):
    """Представление для управления воспитателями"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.selected_teacher = None
        self.page = page
        self.search_query = ""
        
        # Поля формы
        self.last_name_field = ft.TextField(
            label="Фамилия *",
            width=300,
            autofocus=True
        )
        self.last_name_error = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)
        
        self.first_name_field = ft.TextField(
            label="Имя *",
            width=300
        )
        self.first_name_error = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)
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
        
        # Кнопки формы
        self.save_button = ft.ElevatedButton(
            "Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self.save_teacher,
            bgcolor=PRIMARY_COLOR,
            color=ft.Colors.WHITE
        )
        self.cancel_button = ft.OutlinedButton(
            "Отмена",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_edit
        )
        
        # Форма
        self.form_title = ft.Text("Добавить воспитателя", size=20, weight=ft.FontWeight.BOLD)
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
        self.search_bar = SearchBar(on_search=self.on_search, placeholder="Поиск воспитателей...")
        
        # Таблица
        self.data_table = DataTable(
            columns=["№", "ФИО", "Телефон", "Email"],
            rows=[],
            on_edit=self.edit_teacher,
            on_delete=self.delete_teacher
        )
        
        # Кнопка добавления
        add_button = ft.ElevatedButton(
            "Добавить воспитателя",
            icon=ft.Icons.ADD,
            on_click=self.show_add_form,
            bgcolor=PRIMARY_COLOR,
            color=ft.Colors.WHITE
        )
        
        # Загружаем данные
        self.load_teachers()
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("Воспитатели", size=24, weight=ft.FontWeight.BOLD),
                add_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.form_container,
            self.search_bar,
            self.data_table
        ], spacing=20, expand=True)
    
    def on_search(self, query: str):
        """Обработчик поиска"""
        self.search_query = query
        self.load_teachers(query)
    
    def load_teachers(self, search_query: str = ""):
        """Загрузка списка воспитателей"""
        if search_query:
            teachers = self.db.search_teachers(search_query)
        else:
            teachers = self.db.get_all_teachers()
        
        rows = []
        for i, teacher in enumerate(teachers, 1):
            # Формируем данные в новом формате: {"id": ..., "values": [...]}
            rows.append({
                "id": teacher['teacher_id'],
                "values": [
                    str(i), # Порядковый номер
                    teacher.get('full_name', ''),
                    teacher.get('phone', ''),
                    teacher.get('email', '')
                ]
            })
        
        self.data_table.set_rows(rows)
        if self.page:
            self.update()
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_teacher = None
        self.clear_form()
        self.form_title.value = "Добавить воспитателя"
        self.form_container.visible = True
        self.update()
    
    def edit_teacher(self, teacher_id: str):
        """Редактировать воспитателя"""
        teacher = self.db.get_teacher_by_id(int(teacher_id))
        if teacher:
            self.selected_teacher = teacher
            self.last_name_field.value = teacher['last_name']
            self.first_name_field.value = teacher['first_name']
            self.middle_name_field.value = teacher['middle_name'] or ''
            
            # Разбираем телефон на код страны и номер
            phone = teacher['phone'] or ''
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
            
            self.email_field.value = teacher['email'] or ''
            
            self.form_title.value = "Редактировать воспитателя"
            self.form_container.visible = True
            self.update()
    
    def delete_teacher(self, teacher_id: str):
        """Удалить воспитателя"""
        teacher = self.db.get_teacher_by_id(int(teacher_id))
        if not teacher:
            self.show_error("Воспитатель не найден")
            return

        def on_yes(e):
            try:
                groups = [g for g in self.db.get_all_groups() if g['teacher_id'] == int(teacher_id)]
                if groups:
                    group_names = ", ".join(g['group_name'] for g in groups)
                    self.show_error(
                        f"Невозможно удалить воспитателя, так как он закреплен за группами: {group_names}. "
                        "Сначала открепите воспитателя от групп."
                    )
                    return
                self.db.delete_teacher(int(teacher_id))
                self.load_teachers(self.search_query)
                if self.on_refresh:
                    self.on_refresh()
                self.show_success(f"Воспитатель {teacher['full_name']} успешно удален")
            except Exception as ex:
                self.show_error(f"Ошибка при удалении воспитателя: {str(ex)}")

        show_confirm_dialog(
            self.page,
            title="Удаление воспитателя",
            content=f"Вы уверены, что хотите удалить воспитателя {teacher['full_name']}?",
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
    
    def save_teacher(self, e):
        """Сохранить воспитателя"""
        # Проверка обязательных полей
        if not self.validate_fields():
            return
        
        try:
            if self.selected_teacher:
                # Обновление
                # Собираем полный номер телефона
                full_phone = None
                if self.phone_field.value and self.phone_field.value.strip():
                    full_phone = self.country_code_dropdown.value + self.phone_field.value.replace('-', '')
                
                self.db.update_teacher(
                    self.selected_teacher['teacher_id'],
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=full_phone,
                    email=self.email_field.value or None
                )
                self.show_success("Воспитатель успешно обновлен")
            else:
                # Добавление
                # Собираем полный номер телефона
                full_phone = None
                if self.phone_field.value and self.phone_field.value.strip():
                    full_phone = self.country_code_dropdown.value + self.phone_field.value.replace('-', '')
                
                self.db.add_teacher(
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=full_phone,
                    email=self.email_field.value or None
                )
                self.show_success("Воспитатель успешно добавлен")
            
            self.form_container.visible = False
            self.load_teachers(self.search_query)
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

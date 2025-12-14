"""
Представление для управления воспитателями
"""
import flet as ft
from typing import Callable
from components import SearchBar
from dialogs import show_confirm_dialog
from settings.config import PRIMARY_COLOR
from pages_styles.styles import AppStyles


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
        self.last_name_field = AppStyles.text_field("Фамилия", required=True, autofocus=True)
        self.last_name_error = AppStyles.error_text()
        
        self.first_name_field = AppStyles.text_field("Имя", required=True)
        self.first_name_error = AppStyles.error_text()
        self.middle_name_field = AppStyles.text_field("Отчество")
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
        self.email_field = AppStyles.text_field("Email", keyboard_type=ft.KeyboardType.EMAIL)
        
        self.education_field = AppStyles.text_field("Образование", multiline=True, max_lines=3)
        
        self.experience_field = AppStyles.text_field("Стаж работы (лет)", keyboard_type=ft.KeyboardType.NUMBER)
        
        self.birth_date_field = AppStyles.text_field("Дата рождения", hint_text="дд-мм-гггг", max_length=10, on_change=self.format_birth_date)
        
        self.address_field = AppStyles.text_field("Адрес проживания", multiline=True, max_lines=2)
        
        # Кнопки формы
        self.save_button = AppStyles.primary_button("Сохранить", icon=ft.Icons.SAVE, on_click=self.save_teacher)
        self.cancel_button = AppStyles.secondary_button("Отмена", icon=ft.Icons.CANCEL, on_click=self.cancel_edit)
        
        # Форма
        self.form_title = AppStyles.form_title("Добавить воспитателя")
        self.form_container = AppStyles.form_container(
            AppStyles.form_column([
                self.form_title,
                self.last_name_field,
                self.last_name_error,
                self.first_name_field,
                self.first_name_error,
                self.middle_name_field,
                AppStyles.form_row([self.country_code_dropdown, self.phone_field]),
                self.email_field,
                self.birth_date_field,
                self.address_field,
                self.education_field,
                self.experience_field,
                AppStyles.button_row([self.save_button, self.cancel_button])
            ])
        )
        
        # Поиск
        self.search_bar = SearchBar(on_search=self.on_search, placeholder="Поиск воспитателей...")
        
        # Список воспитателей
        self.teachers_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        # Кнопка добавления
        add_button = AppStyles.primary_button("Добавить воспитателя", icon=ft.Icons.ADD, on_click=self.show_add_form)
        
        # Загружаем данные
        self.load_teachers()
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Воспитатели", "Добавить воспитателя", self.show_add_form),
            self.form_container,
            self.search_bar,
            ft.Container(content=self.teachers_list, expand=True)
        ], spacing=20)
        self.expand = True
    
    def on_search(self, query: str):
        """Обработчик поиска"""
        self.search_query = query
        self.load_teachers(query)
    
    def load_teachers(self, search_query: str = ""):
        """Загрузка списка воспитателей"""
        teachers = self.db.search_teachers(search_query) if search_query else self.db.get_all_teachers()
        self.teachers_list.controls = [self._create_teacher_item(teacher) for teacher in teachers]
        if self.page:
            self.page.update()
    
    def _create_teacher_item(self, teacher):
        """Создать элемент списка для воспитателя"""
        phone_text = teacher.get('phone') if teacher.get('phone') else "Не указан"
        email_text = teacher.get('email') if teacher.get('email') else "Не указан"
        
        return ft.ListTile(
            title=ft.Text(teacher.get('full_name', ''), weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"Тел: {phone_text} | Email: {email_text}"),
            trailing=ft.PopupMenuButton(
                tooltip="",
                items=[
                    ft.PopupMenuItem(text="Редактировать", icon=ft.Icons.EDIT, on_click=lambda _, tid=teacher['teacher_id']: self.edit_teacher(str(tid))),
                    ft.PopupMenuItem(text="Удалить", icon=ft.Icons.DELETE, on_click=lambda _, tid=teacher['teacher_id']: self.delete_teacher(str(tid)))
                ]
            )
        )
    
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
            self.birth_date_field.value = teacher.get('birth_date') or ''
            self.address_field.value = teacher.get('address') or ''
            self.education_field.value = teacher.get('education') or ''
            self.experience_field.value = str(teacher.get('experience') or '')
            
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
    
    def format_birth_date(self, e):
        """Форматирование даты рождения в формате дд-мм-гггг"""
        value = e.control.value
        digits = ''.join(filter(str.isdigit, value))
        
        # Ограничиваем до 8 цифр
        if len(digits) > 8:
            digits = digits[:8]
        
        # Применяем маску дд-мм-гггг
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"
        
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
                    email=self.email_field.value or None,
                    birth_date=self.birth_date_field.value or None,
                    address=self.address_field.value or None,
                    education=self.education_field.value or None,
                    experience=int(self.experience_field.value) if self.experience_field.value and self.experience_field.value.isdigit() else None
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
                    email=self.email_field.value or None,
                    birth_date=self.birth_date_field.value or None,
                    address=self.address_field.value or None,
                    education=self.education_field.value or None,
                    experience=int(self.experience_field.value) if self.experience_field.value and self.experience_field.value.isdigit() else None
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
        self.birth_date_field.value = ""
        self.address_field.value = ""
        self.education_field.value = ""
        self.experience_field.value = ""
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

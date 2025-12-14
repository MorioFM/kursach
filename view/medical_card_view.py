"""
Представление для медицинской карты ребёнка
"""
import flet as ft
from typing import Callable
from pages_styles.styles import AppStyles


class MedicalCardView(ft.Container):
    """Представление медицинской карты ребёнка"""
    
    def __init__(self, db, child_id: int, child_name: str, on_close: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.child_id = child_id
        self.child_name = child_name
        self.on_close = on_close
        self.page = page
        
        # Поля формы
        self.blood_type_dropdown = ft.Dropdown(
            label="Группа крови",
            width=350,
            options=[
                ft.DropdownOption("I (0)", "I (0)"),
                ft.DropdownOption("II (A)", "II (A)"),
                ft.DropdownOption("III (B)", "III (B)"),
                ft.DropdownOption("IV (AB)", "IV (AB)")
            ]
        )
        
        self.allergies_field = ft.TextField(
            label="Аллергии",
            width=350,
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Укажите известные аллергии..."
        )
        
        self.chronic_diseases_field = ft.TextField(
            label="Хронические заболевания",
            width=350,
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Укажите хронические заболевания..."
        )
        
        self.vaccinations_field = ft.TextField(
            label="Прививки",
            width=350,
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Список сделанных прививок..."
        )
        
        self.height_field = ft.TextField(
            label="Рост (см)",
            width=170,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="120"
        )
        
        self.weight_field = ft.TextField(
            label="Вес (кг)",
            width=170,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="25.5"
        )
        
        self.doctor_notes_field = ft.TextField(
            label="Заметки врача",
            width=350,
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Дополнительные заметки врача..."
        )
        
        self.emergency_contact_field = ft.TextField(
            label="Экстренный контакт",
            width=350,
            hint_text="+7-XXX-XXX-XX-XX"
        )
        
        self.last_checkup_field = ft.TextField(
            label="Последний осмотр",
            width=350,
            hint_text="дд-мм-гггг",
            max_length=10,
            on_change=self.format_date
        )
        
        # Кнопки
        self.save_button = ft.ElevatedButton(
            "Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self.save_medical_record
        )
        self.close_button = ft.OutlinedButton(
            "Закрыть",
            icon=ft.Icons.CLOSE,
            on_click=self.close_view
        )
        
        # Загружаем данные
        self.load_medical_record()
        
        # Вкладки
        basic_info_tab = ft.Tab(
            text="Основная информация",
            content=ft.Container(
                content=ft.Column([
                    self.blood_type_dropdown,
                    ft.Row([self.height_field, self.weight_field], spacing=10),
                    self.last_checkup_field,
                    self.emergency_contact_field
                ], spacing=15),
                padding=20
            )
        )
        
        diseases_tab = ft.Tab(
            text="Заболевания",
            content=ft.Container(
                content=ft.Column([
                    self.allergies_field,
                    self.chronic_diseases_field,
                    self.vaccinations_field,
                    self.doctor_notes_field
                ], spacing=15),
                padding=20
            )
        )
        
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[basic_info_tab, diseases_tab],
            expand=True
        )
        
        # Основной контент
        self.content = ft.Column([
            tabs,
            ft.Divider(),
            ft.Row([self.save_button, self.close_button], spacing=10)
        ], spacing=10)
        
        self.padding = 20
        self.expand = True
    
    def format_date(self, e):
        """Форматирование даты в формате дд-мм-гггг"""
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
    
    def load_medical_record(self):
        """Загрузить медицинскую карту"""
        record = self.db.get_medical_record(self.child_id)
        if record:
            self.blood_type_dropdown.value = record.get('blood_type')
            self.allergies_field.value = record.get('allergies') or ''
            self.chronic_diseases_field.value = record.get('chronic_diseases') or ''
            self.vaccinations_field.value = record.get('vaccinations') or ''
            self.height_field.value = str(record.get('height')) if record.get('height') else ''
            self.weight_field.value = str(record.get('weight')) if record.get('weight') else ''
            self.doctor_notes_field.value = record.get('doctor_notes') or ''
            self.emergency_contact_field.value = record.get('emergency_contact') or ''
            self.last_checkup_field.value = record.get('last_checkup') or ''
    
    def save_medical_record(self, e):
        """Сохранить медицинскую карту"""
        try:
            # Преобразуем числовые поля
            height = None
            weight = None
            
            if self.height_field.value and self.height_field.value.strip():
                try:
                    height = float(self.height_field.value.replace(',', '.'))
                except:
                    pass
            
            if self.weight_field.value and self.weight_field.value.strip():
                try:
                    weight = float(self.weight_field.value.replace(',', '.'))
                except:
                    pass
            
            # Сохраняем данные
            self.db.create_or_update_medical_record(
                child_id=self.child_id,
                blood_type=self.blood_type_dropdown.value,
                allergies=self.allergies_field.value or None,
                chronic_diseases=self.chronic_diseases_field.value or None,
                vaccinations=self.vaccinations_field.value or None,
                height=height,
                weight=weight,
                doctor_notes=self.doctor_notes_field.value or None,
                emergency_contact=self.emergency_contact_field.value or None,
                last_checkup=self.last_checkup_field.value or None
            )
            
            self.show_success("Медицинская карта успешно сохранена")
            if self.on_close:
                self.on_close()
            
        except Exception as ex:
            self.show_error(f"Ошибка при сохранении: {str(ex)}")
    
    def close_view(self, e):
        """Закрыть представление"""
        if self.on_close:
            self.on_close()
    
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
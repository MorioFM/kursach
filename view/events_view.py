"""
Представление для управления мероприятиями
"""
import flet as ft
from datetime import datetime, date
from typing import Callable

from dialogs import show_confirm_dialog
from pages_styles.styles import AppStyles


class EventsView(ft.Container):
    """Представление для управления мероприятиями"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        self.selected_event = None
        # Используем client_storage для сохранения мероприятий
        if page and hasattr(page, 'client_storage'):
            stored_events = page.client_storage.get("events_storage")
            self.events_storage = stored_events if stored_events else []
        else:
            self.events_storage = []
        
        # Поля формы
        self.event_name_field = AppStyles.text_field("Название мероприятия", required=True, autofocus=True)
        self.event_name_error = AppStyles.error_text()
        
        self.event_date_field = AppStyles.text_field("Дата проведения", required=True, hint_text="дд-мм-гггг", max_length=10, on_change=self.format_event_date)
        self.event_date_error = AppStyles.error_text()
        
        self.description_field = ft.TextField(
            label="Описание",
            width=300,
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        # Выбор ответственного воспитателя
        self.teacher_dropdown = ft.Dropdown(
            label="Ответственный воспитатель",
            width=300,
            options=[]
        )
        
        # Список групп для назначения
        self.groups_list_view = ft.ListView(expand=True, spacing=5)
        self.groups_container = ft.Container(
            content=ft.Column([
                ft.Text("Участвующие группы", weight=ft.FontWeight.BOLD),
                self.groups_list_view
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=5,
            height=200,
            margin=ft.margin.only(top=10)
        )
        
        # Кнопки формы
        self.save_button = AppStyles.primary_button("Сохранить", icon=ft.Icons.SAVE, on_click=self.save_event)
        self.cancel_button = AppStyles.secondary_button("Отмена", icon=ft.Icons.CANCEL, on_click=self.cancel_edit)
        
        # Форма
        self.form_container = AppStyles.form_container(
            ft.Column([
                ft.Text("Добавить мероприятие", size=20, weight=ft.FontWeight.BOLD),
                self.event_name_field,
                self.event_name_error,
                self.event_date_field,
                self.event_date_error,
                self.description_field,
                self.teacher_dropdown,
                self.groups_container,
                AppStyles.button_row([self.save_button, self.cancel_button])
            ], spacing=5)
        )
        
        # Список мероприятий
        self.events_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Мероприятия", "Добавить мероприятие", self.show_add_form),
            self.form_container,
            ft.Container(content=self.events_list, expand=True)
        ], spacing=20)
        self.expand = True
        
        # Загружаем данные без update
        self.events_list.controls.clear()
        for event in self.events_storage:
            self.events_list.controls.append(self._create_event_item(event))
    
    def format_event_date(self, e):
        """Форматирование даты мероприятия в формате дд-мм-гггг"""
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
    
    def load_events(self):
        """Загрузка списка мероприятий"""
        self.events_list.controls.clear()
        for event in self.events_storage:
            self.events_list.controls.append(self._create_event_item(event))
        if self.page:
            self.page.update()
    
    def _create_event_item(self, event):
        """Создать элемент списка для мероприятия"""
        eid = event.get('event_id')
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.EVENT),
            title=ft.Text(event.get('name', '')),
            subtitle=ft.Text(f"Дата: {event.get('date', '')} | Ответственный: {event.get('teacher_name', 'Не назначен')} | Групп: {len(event.get('groups', []))}"),
            trailing=ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                tooltip="",
                items=[
                    ft.PopupMenuItem(text="Участники", icon=ft.Icons.GROUPS, on_click=lambda _, e=eid: self.view_participants(str(e))),
                    ft.PopupMenuItem(text="Редактировать", icon=ft.Icons.EDIT, on_click=lambda _, e=eid: self.edit_event(str(e))),
                    ft.PopupMenuItem(text="Удалить", icon=ft.Icons.DELETE, on_click=lambda _, e=eid: self.delete_event(str(e)))
                ]
            )
        )
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_event = None
        self.clear_form()
        self.form_container.content.controls[0].value = "Добавить мероприятие"
        self.form_container.visible = True
        self._load_teachers_for_form()
        self._load_groups_for_form()
        self.update()
    
    def edit_event(self, event_id: str):
        """Редактировать мероприятие"""
        # Находим мероприятие для редактирования
        event = next((e for e in self.events_storage if e['event_id'] == int(event_id)), None)
        if not event:
            return
            
        self.selected_event = event
        
        # Заполняем поля формы данными мероприятия
        self.event_name_field.value = event.get('name', '')
        self.event_date_field.value = event.get('date', '')
        self.description_field.value = event.get('description', '')
        
        self.form_container.content.controls[0].value = "Редактировать мероприятие"
        self.form_container.visible = True
        self._load_teachers_for_form()
        
        # Устанавливаем выбранного воспитателя
        teacher_id = event.get('teacher_id')
        if teacher_id:
            self.teacher_dropdown.value = str(teacher_id)
        else:
            self.teacher_dropdown.value = "0"
            
        self._load_groups_for_form()
        
        # Отмечаем выбранные группы
        event_groups = event.get('groups', [])
        for checkbox in self.groups_list_view.controls:
            checkbox.value = checkbox.data in event_groups
            
        self.update()
    
    def delete_event(self, event_id: str):
        """Удалить мероприятие"""
        def on_yes(e):
            self.events_storage = [event for event in self.events_storage if event['event_id'] != int(event_id)]
            if self.page and hasattr(self.page, 'client_storage'):
                self.page.client_storage.set("events_storage", self.events_storage)
            self.load_events()
            if self.on_refresh:
                self.on_refresh()

        show_confirm_dialog(
            self.page,
            title="Удаление мероприятия",
            content="Вы уверены, что хотите удалить это мероприятие?",
            on_yes=on_yes,
            adaptive=True
        )
    
    def view_participants(self, event_id: str):
        """Просмотр участников мероприятия"""
        event = next((e for e in self.events_storage if e['event_id'] == int(event_id)), None)
        if not event:
            return
            
        event_groups = event.get('groups', [])
        participants_content = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
        
        for group_id in event_groups:
            group = next((g for g in self.db.get_all_groups() if g['group_id'] == group_id), None)
            if not group:
                continue
                
            children = self.db.get_children_by_group(group_id)
            
            group_card = ft.ExpansionTile(
                title=ft.Text(f"Группа: {group['group_name']}", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"Детей: {len(children)}"),
                controls=[
                    ft.ListTile(
                        title=ft.Text(f"{child['last_name']} {child['first_name']}"),
                        subtitle=ft.Text(f"Возраст: {self._calculate_age(child['birth_date'])} лет")
                    ) for child in children
                ]
            )
            participants_content.controls.append(group_card)
        
        if not event_groups:
            participants_content.controls.append(
                ft.Text("Нет участвующих групп", size=16, color=ft.Colors.GREY)
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Участники мероприятия"),
            content=ft.Container(
                content=participants_content,
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _calculate_age(self, birth_date_str):
        """Вычисление возраста"""
        try:
            if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            else:
                birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
            
            today = date.today()
            return today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        except:
            return 0
    
    def _load_teachers_for_form(self):
        """Загружает список воспитателей в форму"""
        teachers = self.db.get_all_teachers()
        self.teacher_dropdown.options = [
            ft.DropdownOption("0", "Не назначен")
        ] + [
            ft.DropdownOption(str(t['teacher_id']), f"{t['last_name']} {t['first_name']}")
            for t in teachers
        ]
        self.teacher_dropdown.value = "0"
    
    def _load_groups_for_form(self):
        """Загружает список групп в форму для выбора"""
        self.groups_list_view.controls.clear()
        all_groups = self.db.get_all_groups()
        
        for group in all_groups:
            children_count = len(self.db.get_children_by_group(group['group_id']))
            
            checkbox = ft.Checkbox(
                label=f"{group['group_name']} ({children_count} детей)",
                value=False,
                data=group['group_id']
            )
            self.groups_list_view.controls.append(checkbox)
    
    def validate_fields(self):
        """Проверить обязательные поля"""
        self.clear_field_errors()
        is_valid = True
        
        if not self.event_name_field.value or not self.event_name_field.value.strip():
            self.event_name_error.value = "Заполните поле"
            self.event_name_error.visible = True
            is_valid = False
        
        if not self.event_date_field.value or not self.event_date_field.value.strip():
            self.event_date_error.value = "Заполните поле"
            self.event_date_error.visible = True
            is_valid = False
        
        if not is_valid:
            self.update()
        
        return is_valid
    
    def clear_field_errors(self):
        """Очистить все сообщения об ошибках"""
        self.event_name_error.visible = False
        self.event_date_error.visible = False
    
    def save_event(self, e):
        """Сохранить мероприятие"""
        if not self.validate_fields():
            return
        
        try:
            selected_groups = [
                cb.data for cb in self.groups_list_view.controls if cb.value
            ]
            
            teacher_id = int(self.teacher_dropdown.value) if self.teacher_dropdown.value and self.teacher_dropdown.value != "0" else None
            teacher_name = "Не назначен"
            if teacher_id:
                teacher = self.db.get_teacher_by_id(teacher_id)
                if teacher:
                    teacher_name = f"{teacher['last_name']} {teacher['first_name']}"
            
            if self.selected_event:
                # Обновление существующего мероприятия
                new_event = {
                    'event_id': self.selected_event['event_id'],
                    'name': self.event_name_field.value,
                    'date': self.event_date_field.value,
                    'description': self.description_field.value or '',
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name,
                    'groups': selected_groups
                }
                for i, event in enumerate(self.events_storage):
                    if event['event_id'] == self.selected_event['event_id']:
                        self.events_storage[i] = new_event
                        break
            else:
                # Создание нового мероприятия
                new_event = {
                    'event_id': len(self.events_storage) + 1,
                    'name': self.event_name_field.value,
                    'date': self.event_date_field.value,
                    'description': self.description_field.value or '',
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name,
                    'groups': selected_groups
                }
                self.events_storage.append(new_event)
            
            # Сохраняем в client_storage
            if self.page and hasattr(self.page, 'client_storage'):
                self.page.client_storage.set("events_storage", self.events_storage)
            
            self.form_container.visible = False
            self.load_events()
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
        self.event_name_field.value = ""
        self.event_date_field.value = ""
        self.description_field.value = ""
        self.teacher_dropdown.value = "0"
        self.groups_list_view.controls.clear()
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
    
    def refresh(self):
        """Обновить данные"""
        self.load_events()
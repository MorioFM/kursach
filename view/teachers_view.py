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
        self.first_name_field = ft.TextField(
            label="Имя *",
            width=300
        )
        self.middle_name_field = ft.TextField(
            label="Отчество",
            width=300
        )
        self.phone_field = ft.TextField(
            label="Телефон",
            width=300,
            keyboard_type=ft.KeyboardType.PHONE
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
                self.first_name_field,
                self.middle_name_field,
                self.phone_field,
                self.email_field,
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
            self.phone_field.value = teacher['phone'] or ''
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
    
    def save_teacher(self, e):
        """Сохранить воспитателя"""
        # Проверка обязательных полей
        if not self.last_name_field.value or not self.last_name_field.value.strip():
            self.show_error("Поле 'Фамилия' обязательно для заполнения")
            return
        
        if not self.first_name_field.value or not self.first_name_field.value.strip():
            self.show_error("Поле 'Имя' обязательно для заполнения")
            return
        
        try:
            if self.selected_teacher:
                # Обновление
                self.db.update_teacher(
                    self.selected_teacher['teacher_id'],
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=self.phone_field.value or None,
                    email=self.email_field.value or None
                )
                self.show_success("Воспитатель успешно обновлен")
            else:
                # Добавление
                self.db.add_teacher(
                    last_name=self.last_name_field.value,
                    first_name=self.first_name_field.value,
                    middle_name=self.middle_name_field.value or None,
                    phone=self.phone_field.value or None,
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
        self.phone_field.value = ""
        self.email_field.value = ""
    
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

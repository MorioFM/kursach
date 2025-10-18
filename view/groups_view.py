"""
Представление для управления группами
"""
import flet as ft
from typing import Callable
from components import DataTable, InfoCard
from dialogs import show_confirm_dialog
from settings.config import AGE_CATEGORIES


class GroupsView(ft.Container):
    """Представление для управления группами"""
    
    def __init__(self, db, on_refresh: Callable = None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.selected_group = None
        
        # Поля формы
        self.group_name_field = ft.TextField(
            label="Название группы",
            width=300,
            autofocus=True
        )
        self.age_category_dropdown = ft.Dropdown(
            label="Возрастная категория",
            width=300,
            options=[ft.DropdownOption(k, v) for k, v in AGE_CATEGORIES.items()]
        )
        self.teacher_dropdown = ft.Dropdown(
            label="Воспитатель",
            width=300,
            options=[]
        )

        # Кнопки формы
        self.save_button = ft.ElevatedButton(
            "Сохранить",
            icon=ft.Icons.SAVE,
            on_click=self.save_group
        )
        self.cancel_button = ft.OutlinedButton(
            "Отмена",
            icon=ft.Icons.CANCEL,
            on_click=self.cancel_edit
        )
        
        # Форма
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Добавить группу", size=20, weight=ft.FontWeight.BOLD),
                self.group_name_field,
                self.age_category_dropdown,
                self.teacher_dropdown,
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
        
        # Таблица
        self.data_table = DataTable(
            columns=["ID", "Название", "Возрастная категория", "Воспитатель", "Кол-во детей"],
            rows=[],
            on_edit=self.edit_group,
            on_delete=self.delete_group
        )
        
        # Статистика
        self.stats_container = ft.Row(spacing=20, wrap=True)
        
        # Кнопка добавления
        add_button = ft.ElevatedButton(
            "Добавить группу",
            icon=ft.Icons.ADD,
            on_click=self.show_add_form
        )
        
        # Загружаем данные
        self.load_teachers()
        self.load_groups()
        self.load_stats()
        
        self.content = ft.Column([
            ft.Row([
                ft.Text("Группы", size=24, weight=ft.FontWeight.BOLD),
                add_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.form_container,
            self.stats_container,
            self.data_table
        ], spacing=20, expand=True)
    
    def load_groups(self):
        """Загрузка списка групп"""
        groups = self.db.get_all_groups()
        
        rows = []
        for group in groups:
            teacher_name = group.get('teacher_name', 'Не назначен')
            rows.append([
                str(group['group_id']),
                group['group_name'],
                AGE_CATEGORIES.get(group['age_category'], group['age_category']),
                teacher_name,
                str(group.get('children_count', 0))
            ])
        
        self.data_table.set_rows(rows)
        if self.page:
            self.update()
    
    def load_stats(self):
        """Загрузка статистики"""
        stats = self.db.get_statistics()
        
        self.stats_container.controls = [
            InfoCard("Всего групп", str(stats['total_groups']), ft.Icons.GROUPS),
            InfoCard("Всего детей", str(stats['total_children']), ft.Icons.CHILD_CARE),
            InfoCard("Средний возраст", f"{stats['average_age']:.1f} лет", ft.Icons.CAKE)
        ]
        
        if self.page:
            self.update()
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_group = None
        self.clear_form()
        self.load_teachers()
        self.form_container.content.controls[0].value = "Добавить группу"
        self.form_container.visible = True
        self.update()
    
    def edit_group(self, group_id: str):
        """Редактировать группу"""
        group = self.db.get_group_by_id(int(group_id))
        if group:
            self.selected_group = group
            self.group_name_field.value = group['group_name']
            self.age_category_dropdown.value = group['age_category']
            self.teacher_dropdown.value = str(group['teacher_id']) if group['teacher_id'] else "0"
            
            self.load_teachers()
            self.form_container.content.controls[0].value = "Редактировать группу"
            self.form_container.visible = True
            self.update()
    
    def delete_group(self, group_id: str):
        """Удалить группу"""
        def on_yes(e):
            try:
                self.db.delete_group(int(group_id))
                self.load_groups()
                self.load_stats()
                if self.on_refresh:
                    self.on_refresh()
            except Exception as ex:
                self.show_error(f"Ошибка при удалении: {str(ex)}")

        show_confirm_dialog(
            self.page,
            title="Удаление группы",
            content="Вы уверены, что хотите удалить эту группу? Все дети будут откреплены от группы.",
            on_yes=on_yes,
            adaptive=True,
        )
    
    def save_group(self, e):
        """Сохранить группу"""
        # Валидация
        if not all([
            self.group_name_field.value,
            self.age_category_dropdown.value
        ]):
            self.show_error("Пожалуйста, заполните все обязательные поля")
            return
        
        try:
            teacher_id = None
            if self.teacher_dropdown.value and self.teacher_dropdown.value != "0":
                teacher_id = int(self.teacher_dropdown.value)
            
            if self.selected_group:
                # Обновление
                self.db.update_group(
                    self.selected_group['group_id'],
                    group_name=self.group_name_field.value,
                    age_category=self.age_category_dropdown.value,
                    teacher_id=teacher_id
                )
            else:
                # Добавление
                self.db.add_group(
                    group_name=self.group_name_field.value,
                    age_category=self.age_category_dropdown.value,
                    teacher_id=teacher_id
                )

            self.form_container.visible = False
            self.load_groups()
            self.load_stats()
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
        self.group_name_field.value = ""
        self.age_category_dropdown.value = None
        self.teacher_dropdown.value = "0"

    def load_teachers(self):
        """Загрузка списка воспитателей для выпадающего списка"""
        teachers = self.db.get_all_teachers()
        self.teacher_dropdown.options = [
            ft.DropdownOption(key=str(t['teacher_id']), text=t['full_name'])
            for t in teachers
        ]
        # Добавляем опцию "Не назначен"
        self.teacher_dropdown.options.insert(0, ft.DropdownOption(key="0", text="Не назначен"))
        
        if self.page:
            self.update()
    
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
        self.load_groups()
        self.load_stats()

"""
Представление для управления группами
"""
import flet as ft
from typing import Callable
from components import InfoCard
from dialogs import show_confirm_dialog
from settings.config import AGE_CATEGORIES
from pages_styles.styles import AppStyles


class GroupsView(ft.Container):
    """Представление для управления группами"""
    
    def __init__(self, db, on_refresh: Callable = None, page=None):
        super().__init__()
        self.db = db
        self.on_refresh = on_refresh
        self.page = page
        self.selected_group = None
        
        # Поля формы
        self.group_name_field = AppStyles.text_field("Название группы", required=True, autofocus=True)
        self.group_name_error = AppStyles.error_text()
        
        self.age_category_dropdown = AppStyles.dropdown_field("Возрастная категория", [ft.DropdownOption(k, v) for k, v in AGE_CATEGORIES.items()], required=True)
        self.age_category_error = AppStyles.error_text()
        self.teacher_dropdown = ft.Dropdown(
            label="Воспитатель",
            width=300,
            options=[]
        )

        # Список детей для назначения в группу
        self.children_list_view = ft.ListView(expand=True, spacing=5)
        self.children_container = ft.Container(
            content=ft.Column([
                ft.Text("Дети в группе", weight=ft.FontWeight.BOLD),
                self.children_list_view
            ]),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=5,
            height=200,
            margin=ft.margin.only(top=10)
        )

        # Кнопки формы
        self.save_button = AppStyles.primary_button("Сохранить", icon=ft.Icons.SAVE, on_click=self.save_group)
        self.cancel_button = AppStyles.secondary_button("Отмена", icon=ft.Icons.CANCEL, on_click=self.cancel_edit)
        
        # Форма
        self.form_container = ft.Container(
            content=ft.Column([
                ft.Text("Добавить группу", size=20, weight=ft.FontWeight.BOLD),
                self.group_name_field,
                self.group_name_error,
                self.age_category_dropdown,
                self.age_category_error,
                self.teacher_dropdown,
                self.children_container,
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
        
        # Список групп
        self.groups_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        self.content = AppStyles.form_column([
            AppStyles.page_header("Группы", "Добавить группу", self.show_add_form),
            self.form_container,
            ft.Container(content=self.groups_list, expand=True)
        ], spacing=20)
        self.expand = True
    
    def show_teacher_info(self, teacher_id):
        """Показать информацию о воспитателе"""
        try:
            teacher = self.db.get_teacher_by_id(teacher_id)
            if not teacher:
                return
            
            dialog = ft.AlertDialog(
                title=ft.Text("Информация о воспитателе"),
                content=ft.Column([
                    ft.Text(f"ФИО: {teacher.get('last_name', '')} {teacher.get('first_name', '')} {teacher.get('middle_name', '') or ''}"),
                    ft.Text(f"Телефон: {teacher.get('phone') or 'Не указан'}"),
                    ft.Text(f"Email: {teacher.get('email') or 'Не указан'}"),
                    ft.Text(f"Образование: {teacher.get('education') or 'Не указано'}"),
                    ft.Text(f"Опыт работы: {teacher.get('experience') or 0} лет")
                ], tight=True),
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda e: self.close_dialog())
                ]
            )
            
            if self.page:
                self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
                
        except Exception as ex:
            print(f"Ошибка получения информации о воспитателе: {ex}")
    
    def close_dialog(self):
        """Закрыть диалог"""
        if self.page and self.page.overlay:
            self.page.overlay.clear()
            self.page.update()
    
    def load_groups(self):
        """Загрузка списка групп"""
        groups = self.db.get_all_groups()
        self.groups_list.controls = [self._create_group_item(group) for group in groups]
        if self.page:
            self.page.update()
    
    def _create_group_item(self, group):
        """Создать элемент списка для группы"""
        teacher_name = group.get('teacher_name', 'Не назначен')
        try:
            children_count = len(self.db.get_children_by_group(group['group_id']))
        except Exception:
            children_count = group.get('children_count', 0)
        
        return ft.ListTile(
            title=ft.Text(group['group_name'], weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"{AGE_CATEGORIES.get(group['age_category'], group['age_category'])} | {teacher_name} | Детей: {children_count}"),
            trailing=ft.PopupMenuButton(
                tooltip="",
                items=[
                    ft.PopupMenuItem(text="Редактировать", icon=ft.Icons.EDIT, on_click=lambda _, gid=group['group_id']: self.edit_group(str(gid))),
                    ft.PopupMenuItem(text="Удалить", icon=ft.Icons.DELETE, on_click=lambda _, gid=group['group_id']: self.delete_group(str(gid)))
                ]
            )
        )
    
    def show_add_form(self, e):
        """Показать форму добавления"""
        self.selected_group = None
        self.clear_form()
        self.load_teachers()
        self.form_container.content.controls[0].value = "Добавить группу"
        self.form_container.visible = True
        self._load_children_for_form()
        if self.page:
            self.page.update()
    
    def edit_group(self, group_id: str):
        """Редактировать группу"""
        group = self.db.get_group_by_id(int(group_id))
        if group:
            self.selected_group = group
            self.group_name_field.value = group['group_name']
            self.age_category_dropdown.value = group['age_category']
            self.teacher_dropdown.value = str(group['teacher_id']) if group['teacher_id'] else "0"
            
            self.load_teachers()
            self._load_children_for_form(group_id=int(group_id))
            self.form_container.content.controls[0].value = "Редактировать группу"
            self.form_container.visible = True
            if self.page:
                self.page.update()
    
    def delete_group(self, group_id: str):
        """Удалить группу"""
        def on_yes(e):
            try:
                self.db.delete_group(int(group_id))
                self.load_groups()
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
    
    def clear_field_errors(self):
        """Очистить все сообщения об ошибках"""
        self.group_name_error.visible = False
        self.age_category_error.visible = False
    
    def validate_fields(self):
        """Проверить обязательные поля и показать ошибки"""
        self.clear_field_errors()
        is_valid = True
        
        if not self.group_name_field.value or not self.group_name_field.value.strip():
            self.group_name_error.value = "Заполните поле"
            self.group_name_error.visible = True
            is_valid = False
        
        if not self.age_category_dropdown.value:
            self.age_category_error.value = "Заполните поле"
            self.age_category_error.visible = True
            is_valid = False
        
        if not is_valid:
            if self.page:
                self.page.update()
        
        return is_valid
    
    def save_group(self, e):
        """Сохранить группу"""
        # Проверка обязательных полей
        if not self.validate_fields():
            return
        
        try:
            teacher_id = None
            if self.teacher_dropdown.value and self.teacher_dropdown.value != "0":
                teacher_id = int(self.teacher_dropdown.value)
            
            new_group_id = None
            if self.selected_group:
                # Обновление
                group_id = self.selected_group['group_id']
                self.db.update_group(
                    group_id,
                    group_name=self.group_name_field.value,
                    age_category=self.age_category_dropdown.value,
                    teacher_id=teacher_id
                )
                new_group_id = group_id
            else:
                # Добавление
                new_group_id = self.db.add_group(
                    group_name=self.group_name_field.value,
                    age_category=self.age_category_dropdown.value,
                    teacher_id=teacher_id
                )

            # Обновляем состав группы
            if new_group_id:
                self._update_group_children(new_group_id)

            self.form_container.visible = False
            self.load_groups()
            if self.on_refresh:
                self.on_refresh()
            if self.page:
                self.page.update()
            
        except Exception as ex:
            self.show_error(f"Ошибка при сохранении: {str(ex)}")
    
    def cancel_edit(self, e):
        """Отменить редактирование"""
        self.form_container.visible = False
        self.clear_form()
        if self.page:
            self.page.update()
    
    def clear_form(self):
        """Очистить форму"""
        self.group_name_field.value = ""
        self.age_category_dropdown.value = None
        self.teacher_dropdown.value = "0"
        self.children_list_view.controls.clear()
        self.clear_field_errors()

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
            self.page.update()
    
    def _load_children_for_form(self, group_id: int | None = None):
        """Загружает список детей в форму для выбора."""
        from datetime import datetime, date
        
        self.children_list_view.controls.clear()
        all_children = self.db.get_all_children()
        
        children_in_group_ids = []
        if group_id:
            children_in_group = self.db.get_children_by_group(group_id)
            children_in_group_ids = [c['child_id'] for c in children_in_group]

        for child in all_children:
            # Показываем всех детей, но делаем недоступными тех, кто уже в других группах
            child_group_id = child.get('group_id')
            is_in_current_group = child['child_id'] in children_in_group_ids
            is_in_other_group = child_group_id is not None and child_group_id != group_id
            
            # Формируем полное имя
            last_name = child.get('last_name', '')
            first_name = child.get('first_name', '')
            middle_name = child.get('middle_name', '')
            full_name = f"{last_name} {first_name} {middle_name}".strip()
            
            # Вычисляем возраст
            try:
                birth_date_str = child['birth_date']
                if '-' in birth_date_str and len(birth_date_str.split('-')[0]) == 4:
                    birth_date_obj = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                else:
                    birth_date_obj = datetime.strptime(birth_date_str, "%d-%m-%Y").date()
                
                today = date.today()
                age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
                full_name += f" ({age} лет)"
            except:
                pass
            
            # Добавляем информацию о группе, если ребенок в другой группе
            if is_in_other_group:
                group_name = child.get('group_name', 'Неизвестная группа')
                full_name += f" (в группе: {group_name})"
            
            checkbox = ft.Checkbox(
                label=full_name,
                value=is_in_current_group,
                data=child['child_id'],
                disabled=is_in_other_group  # Отключаем детей из других групп
            )
            self.children_list_view.controls.append(checkbox)

    def _update_group_children(self, group_id: int):
        """Обновляет состав детей в группе на основе выбора в форме."""
        selected_child_ids = {
            cb.data for cb in self.children_list_view.controls if cb.value
        }
        
        # Получаем текущий список детей в группе
        current_children_in_group = self.db.get_children_by_group(group_id)
        current_child_ids = {c['child_id'] for c in current_children_in_group}

        # Дети, которых нужно добавить
        to_add = selected_child_ids - current_child_ids
        for child_id in to_add:
            self._assign_child(child_id, group_id)

        # Дети, которых нужно убрать
        to_remove = current_child_ids - selected_child_ids
        for child_id in to_remove:
            self._assign_child(child_id, None) # Открепляем от группы

    def show_error(self, message: str):
        """Показать ошибку"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.ERROR
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def add_child_to_group(self, child):
        """
        Открыть диалог для назначения ребёнка в группу.
        `child` может быть id (int/str) или словарь с ключом 'child_id'.
        Этот метод вызывается из children_view.py
        """
        # Определяем id ребёнка
        if isinstance(child, (int, str)):
            child_id = int(child)
        else:
            child_id = int(child.get('child_id'))

        # Собираем варианты групп
        groups = self.db.get_all_groups()
        options = [
            ft.DropdownOption(key=str(g['group_id']), text=g['group_name'])
            for g in groups
        ]
        # опция "Не назначен"
        options.insert(0, ft.DropdownOption(key="0", text="Не назначен"))

        # Предустановка значения (если уже выбрана группа в представлении)
        initial_value = None
        if self.selected_group:
            initial_value = str(self.selected_group.get('group_id'))

        group_dropdown = ft.Dropdown(
            label="Выберите группу",
            options=options,
            value=initial_value or "0",
            width=400
        )

        def on_assign(e):
            try:
                selected = group_dropdown.value
                group_id = None if not selected or selected == "0" else int(selected)
                self._assign_child(child_id, group_id)
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.show_error(f"Ошибка при назначении ребёнка: {str(ex)}")

        def on_cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Назначить ребёнка в группу"),
            content=ft.Column([ft.Text(f"ID ребёнка: {child_id}"), group_dropdown], spacing=10),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.ElevatedButton("Назначить", on_click=on_assign)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _assign_child(self, child_id: int, group_id: int | None):
        """
        Выполнить изменение группы для ребёнка в БД.
        Пытаемся несколько возможных вызовов БД, чтобы быть совместимыми с разным API.
        """
        # Попытки разных имен методов (assign_child_to_group, update_child, update_child_group)
        last_err = None
        try:
            # Предпочтительный метод
            if hasattr(self.db, "assign_child_to_group"):
                self.db.assign_child_to_group(child_id, group_id)
                last_err = None
            else:
                raise AttributeError
        except Exception as ex1:
            last_err = ex1
            try:
                # Частый вариант: update_child(child_id, group_id=...)
                if hasattr(self.db, "update_child"):
                    # Некоторые реализации ожидают dict/kwargs
                    try:
                        self.db.update_child(child_id, group_id=group_id)
                    except TypeError:
                        # Попробуем словарь
                        self.db.update_child(child_id, {"group_id": group_id})
                    last_err = None
                else:
                    raise AttributeError
            except Exception as ex2:
                last_err = ex2
                try:
                    # Ещё вариант: update_child_group(child_id, group_id)
                    if hasattr(self.db, "update_child_group"):
                        self.db.update_child_group(child_id, group_id)
                        last_err = None
                    else:
                        raise AttributeError
                except Exception as ex3:
                    last_err = ex3

        if last_err:
            raise last_err

        # Обновляем данные в представлении
        self.load_groups()
        if self.on_refresh:
            self.on_refresh()
        if self.page:
            self.page.update()

    def refresh(self):
        """Обновить данные"""
        self.load_groups()

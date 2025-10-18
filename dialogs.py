import flet as ft

def show_confirm_dialog(page, title, content, on_yes, on_no=None, adaptive=True):
    """
    Универсальный диалог подтверждения действия (Material/Cupertino/Adaptive)
    :param page: страница Flet
    :param title: заголовок
    :param content: текст
    :param on_yes: функция-обработчик для кнопки Да
    :param on_no: функция-обработчик для кнопки Нет (опционально)
    :param adaptive: использовать ли adaptive-режим
    """
    def handle_yes(e):
        page.close(dialog)
        if on_yes:
            on_yes(e)
    def handle_no(e):
        page.close(dialog)
        if on_no:
            on_no(e)

    material_actions = [
        ft.TextButton(text="Да", on_click=handle_yes),
        ft.TextButton(text="Нет", on_click=handle_no),
    ]
    cupertino_actions = [
        ft.CupertinoDialogAction(
            text="Да",
            is_destructive_action=True,
            on_click=handle_yes,
        ),
        ft.CupertinoDialogAction(
            text="Нет",
            is_default_action=False,
            on_click=handle_no,
        ),
    ]
    if adaptive:
        actions = (
            cupertino_actions
            if page.platform in [ft.PagePlatform.IOS, ft.PagePlatform.MACOS]
            else material_actions
        )
    else:
        actions = material_actions

    dialog = ft.AlertDialog(
        adaptive=adaptive,
        title=ft.Text(title),
        content=ft.Text(content),
        actions=actions,
    )
    page.open(dialog)

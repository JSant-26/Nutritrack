import flet as ft

def crear_navbar(page: ft.Page, selected_index=0):
    def cambiar_pestana(e):
        # Aquí manejas la lógica de navegación global
        idx = e.control.selected_index
        if idx == 0:
            page.go("/home")
        elif idx == 1:
            page.go("/registro")  
        elif idx == 2:
            page.go("/plan")
        elif idx == 3:
            page.go("/perfil")
        page.update()

    return ft.NavigationBar(
        selected_index=selected_index,
        bgcolor="#0c0e16",
        on_change=cambiar_pestana,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME_ROUNDED, label="Inicio"),
            ft.NavigationDestination(icon=ft.icons.FASTFOOD_ROUNDED, label="Registrar"),
            ft.NavigationDestination(icon=ft.icons.LIST_ALT_ROUNDED, label="Plan"),
            ft.NavigationDestination(icon=ft.icons.ACCOUNT_CIRCLE_ROUNDED, label="Perfil"),
        ]
    )
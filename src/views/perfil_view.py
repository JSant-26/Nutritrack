import flet as ft

def PerfilView(page: ft.Page):
    # Aquí puedes recuperar los datos actuales del usuario si los necesitas
    user_email = page.user_data.get("email", "Usuario")
    
    # Definimos la estructura de la vista de perfil
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.Text("Configuración de Perfil", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            
            ft.CircleAvatar(
                content=ft.Icon(ft.icons.PERSON, size=50),
                radius=50,
                bgcolor=ft.colors.GREY_800,
            ),
            
            ft.Text(f"Email: {user_email}", size=16, color=ft.colors.GREY_400),
            
            ft.Divider(height=20, color="rgba(255,255,255,0.1)"),
            
            ft.TextField(label="Peso (kg)", hint_text="Ej: 70", width=300),
            ft.TextField(label="Altura (cm)", hint_text="Ej: 175", width=300),
            ft.TextField(label="Edad", hint_text="Ej: 25", width=300),
            
            ft.ElevatedButton(
                text="Guardar Cambios",
                icon=ft.icons.SAVE_ROUNDED,
                style=ft.ButtonStyle(bgcolor="#6ee7b7", color="#0c0e16"),
                width=300,
                height=45
            ),
            
            ft.TextButton(
                "Cerrar Sesión",
                icon=ft.icons.LOGOUT_ROUNDED,
                on_click=lambda _: [page.user_data.clear(), page.go("/")],
                style=ft.ButtonStyle(color=ft.colors.RED_300)
            )
        ]
    )
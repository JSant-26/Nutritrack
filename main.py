import flet as ft

def main(page: ft.Page):
    page.title = "Nutritrack - Estable"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Restablecemos las dimensiones del teléfono que ahora sí van a funcionar
    page.window.width = 400
    page.window.height = 800
    page.window.resizable = False
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    email_input = ft.TextField(
        label="Correo Electrónico",
        border_color=ft.colors.GREEN_400,
        focused_border_color=ft.colors.GREEN_ACCENT_400,
        width=300
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.colors.GREEN_400,
        focused_border_color=ft.colors.GREEN_ACCENT_400,
        width=300
    )

    page.add(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.icons.TRACK_CHANGES, size=60, color=ft.colors.GREEN_ACCENT_400),
                ft.Text("NUTRITRACK", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                email_input,
                password_input,
                ft.ElevatedButton(
                    text="Iniciar Sesión", 
                    width=200,
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.GREEN_ACCENT_700,
                        color=ft.colors.WHITE
                    )
                )
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
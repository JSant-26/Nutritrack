import flet as ft

def LoginView(page: ft.Page, navegar_a):
    page.clean()

    email_input = ft.TextField(
        label="Correo Electrónico",
        keyboard_type=ft.KeyboardType.EMAIL,
        border_color="green400",
        focused_border_color="greenaccent400",
        width=300
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color="green400",
        focused_border_color="greenaccent400",
        width=300
    )

    def handle_login(e):
        if email_input.value and password_input.value:
            navegar_a("/home")

    # Creamos un layout de seguridad con dimensiones fijas e inyectamos el fondo oscuro
    layout_seguro = ft.Container(
        width=page.window.width,
        height=page.window.height,
        bgcolor="#111111",  # Forzamos el color oscuro nativo de fondo
        alignment=ft.Alignment(0, 0),  # Centrado absoluto
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon("analytics", size=60, color="greenaccent400"),
                ft.Text("NUTRITRACK", size=28, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text("Controla tu evolución, alcanza tus metas", size=12, color="grey400", italic=True),
                ft.Divider(height=10, color="transparent"),
                email_input,
                password_input,
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    width=200,
                    style=ft.ButtonStyle(
                        bgcolor="greenaccent700",
                        color="white"
                    ),
                    on_click=handle_login
                )
            ]
        )
    )

    # Añadimos el layout rígido y forzamos la actualización inmediata del motor gráfico
    page.add(layout_seguro)
    page.update()
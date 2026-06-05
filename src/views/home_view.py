import flet as ft

def HomeView(page: ft.Page, navegar_a):
    page.add(
        ft.Column(
            spacing=0,
            controls=[
                # Barra superior personalizada
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("  Nutritrack", weight=ft.FontWeight.BOLD, size=20),
                            ft.IconButton(icon="logout", on_click=lambda _: navegar_a("/"))                         ]
                    ),
                    bgcolor="surfacevariant",
                    padding=10
                ),
                # Contenido del Dashboard
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text("Resumen Diario", size=24, weight=ft.FontWeight.W_600),
                            ft.Card(
                                color="grey900",
                                content=ft.Container(
                                    padding=15,
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Calorías Restantes", size=14, color="grey400"),
                                            ft.Text("2,000 kcal", size=28, weight=ft.FontWeight.BOLD, color="greenaccent400"),
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )
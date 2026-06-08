import flet as ft
from src.views.login_view import LoginView
from src.views.home_view import HomeView
from src.views.registro_view import RegistroView
from src.views.perfil_view import PerfilView
from src.views.survey_view import SurveyView
from src.views.plan_view import PlanView
from src.components.navbar import crear_navbar

def main(page: ft.Page):
    page.title = "Nutritrack"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 450
    page.window.height = 800
    page.user_data = {"id": None, "email": None}

    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(LoginView(page))
        elif page.route == "/home":
            # HomeView ya devuelve el ft.View completo, solo añade ese objeto
            page.views.append(HomeView(page))
        elif page.route == "/registro":
            page.views.append(
                ft.View(
                    route="/registro",
                    navigation_bar=crear_navbar(page, selected_index=1),
                    controls=[
                        ft.Container(
                            content=ft.Column(controls=[RegistroView(page)], scroll=ft.ScrollMode.AUTO, expand=True),
                            padding=20,
                            expand=True
                        )
                    ]
                )
            )
        elif page.route == "/plan":
            page.views.append(
                ft.View(
                    route="/plan",
                    navigation_bar=crear_navbar(page, selected_index=2),
                    controls=[
                        ft.Container(
                            content=ft.Column(controls=[PlanView(page)], scroll=ft.ScrollMode.AUTO, expand=True),
                            padding=20,
                            expand=True
                        )
                    ]
                )
            )
        elif page.route == "/perfil":
            page.views.append(
                ft.View(
                    route="/perfil",
                    navigation_bar=crear_navbar(page, selected_index=3),
                    controls=[
                        ft.Container(
                            content=ft.Column(controls=[PerfilView(page)], scroll=ft.ScrollMode.AUTO, expand=True),
                            padding=20,
                            expand=True
                        )
                    ]
                )
            )
        elif page.route == "/survey":
            page.views.append(SurveyView(page))
        
        page.update()

    page.on_route_change = route_change
    page.go("/") 

if __name__ == "__main__":
    ft.app(target=main)
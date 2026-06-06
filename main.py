import flet as ft
from src.views.login_view import LoginView
from src.views.survey_view import SurveyView  
from src.views.home_view import HomeView

def main(page: ft.Page):
    page.title = "Nutritrack"

# --- AJUSTES DE PANTALLA PROFESIONALES ---
    page.window_width = 1000        # Ancho inicial cómodo
    page.window_height = 750       # Alto inicial para que quepa todo
    page.window_min_width = 600    # Ancho mínimo permitido al estirar
    page.window_min_height = 550   # Alto mínimo permitido
    page.scroll = ft.ScrollMode.AUTO # Activa barra de scroll automática si la pantalla se encoge
    
    # Este diccionario guardará el ID del usuario de Firebase de forma global
    page.user_data = {"id": None}

    # Manejador de cambios de ruta
    def route_change(route):
        page.views.clear()
        
        if page.route == "/" or page.route == "/login":
            page.views.append(LoginView(page))
        elif page.route == "/survey":
            page.views.append(SurveyView(page))
        elif page.route == "/home": 
            page.views.append(HomeView(page))
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
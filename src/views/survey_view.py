import os
import flet as ft
import pyrebase
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

db = pyrebase.initialize_app(firebase_config).database()

def SurveyView(page: ft.Page):
    # Campos de texto
    edad_input = ft.TextField(label="Edad", width=300, value="21")
    peso_input = ft.TextField(label="Peso (kg)", width=300, value="64")
    altura_input = ft.TextField(label="Altura (cm)", width=300, value="1.70")
    
    objetivo_dropdown = ft.Dropdown(
        label="Objetivo Principal",
        width=300,
        options=[
            ft.dropdown.Option("Ganar Masa Muscular"),
            ft.dropdown.Option("Perder Peso"),
            ft.dropdown.Option("Mantenerse Saludable")
        ],
        value="Ganar Masa Muscular"
    )

    def mostrar_mensaje(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto), show_close_icon=True)
        page.snack_bar.open = True
        page.update()

    def enviar_encuesta(e):
        # Validación simple
        if not edad_input.value or not peso_input.value or not altura_input.value:
            mostrar_mensaje("Por favor, llena todos los campos.")
            return

        # Obtenemos el ID del usuario logueado en la sesión anterior
        user_id = page.user_data.get("id", "usuario_anonimo")

        datos_nutricionales = {
            "edad": edad_input.value,
            "peso": peso_input.value,
            "altura": altura_input.value,
            "objetivo": objetivo_dropdown.value
        }

        try:
            # Intentamos guardar en la ruta: /usuarios/ID_DEL_USUARIO/perfil
            db.child("usuarios").child(user_id).child("perfil").set(datos_nutricionales)
            mostrar_mensaje("¡Perfil guardado con éxito en Firebase!")
            
            page.go("/home") 
            
        except Exception as ex:
            # Si se queda congelado o falla, el mensaje nos dirá exactamente por qué
            print("ERROR DETECTADO EN SURVEY:", str(ex))
            mostrar_mensaje(f"Error al guardar datos: Revisa las Reglas de Firebase.")

    return ft.View(
        route="/survey",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            # Usamos una columna con Scroll automático para que nunca se desborde la interfaz
            ft.Column(
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Icon(ft.icons.ASSIGNMENT, size=60, color=ft.colors.GREEN_ACCENT_400),
                    ft.Text("Perfil Nutricional", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Container(height=10),
                    edad_input,
                    peso_input,
                    altura_input,
                    objetivo_dropdown,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        text="Finalizar Registro",
                        width=250,
                        style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_700, color=ft.colors.WHITE),
                        on_click=enviar_encuesta
                    )
                ]
            )
        ]
    )
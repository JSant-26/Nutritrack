import os
import flet as ft
import pyrebase
from dotenv import load_dotenv

# Cargar variables de entorno
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

# Inicializamos tanto Auth como la Base de Datos
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database() # <-- Añadimos esto para poder consultar la BD desde el Login

def LoginView(page: ft.Page):
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

    def mostrar_mensaje(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto), show_close_icon=True)
        page.snack_bar.open = True
        page.update()

    # Lógica INTRILIGENTE para INICIAR SESIÓN
    def login_usuario(e):
        if not email_input.value or not password_input.value:
            mostrar_mensaje("Por favor, completa todos los campos.")
            return
        try:
            # 1. Autenticar con Firebase Auth
            user = auth.sign_in_with_email_and_password(email_input.value, password_input.value)
            user_id = user['localId']
            page.user_data["id"] = user_id
            page.user_data["email"] = email_input.value
            
            # 2. Consultar la Realtime Database para ver si ya tiene perfil guardado
            perfil_existente = db.child("usuarios").child(user_id).child("perfil").get().val()
            
            if perfil_existente:
                # Si ya tiene datos (Edad, Peso, etc.), va directo al Home
                mostrar_mensaje("¡Bienvenido de vuelta!")
                page.go("/home")
            else:
                # Si es un usuario registrado pero sin datos, va a la encuesta
                mostrar_mensaje("Por favor, completa tu perfil nutricional.")
                page.go("/survey")
                
        except Exception as ex:
            print("ERROR LOGIN:", str(ex))
            mostrar_mensaje("Error al iniciar sesión: Usuario o contraseña incorrectos.")

    def registrar_usuario(e):
        if not email_input.value or not password_input.value:
            mostrar_mensaje("Por favor, completa todos los campos.")
            return
        if len(password_input.value) < 6:
            mostrar_mensaje("La contraseña debe tener al menos 6 caracteres.")
            return
        try:
            user = auth.create_user_with_email_and_password(email_input.value, password_input.value)
            page.user_data["id"] = user['localId']
            mostrar_mensaje("¡Usuario registrado con éxito!")
            page.go("/survey")  # Al registrarse por primera vez, siempre va a la encuesta
        except Exception as ex:
            mostrar_mensaje("Error al registrar: El correo ya está en uso o no es válido.")

    return ft.View(
        route="/",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Icon(ft.icons.TRACK_CHANGES, size=60, color=ft.colors.GREEN_ACCENT_400),
                    ft.Text("NUTRITRACK", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Container(height=10),
                    email_input,
                    password_input,
                    ft.Container(height=10),
                    
                    ft.ElevatedButton(
                        text="Iniciar Sesión", 
                        width=250,
                        style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_700, color=ft.colors.WHITE),
                        on_click=login_usuario
                    ),
                    
                    ft.TextButton(
                        text="¿No tienes cuenta? Regístrate aquí",
                        style=ft.ButtonStyle(color=ft.colors.GREEN_400),
                        on_click=registrar_usuario
                    )
                ]
            )
        ]
    )
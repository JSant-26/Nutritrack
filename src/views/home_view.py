import os
import flet as ft
import pyrebase
import threading
from datetime import datetime
from dotenv import load_dotenv
from src.services.food_api import FatSecretAPI
from src.components.navbar import crear_navbar
from src.views.registro_view import RegistroView
from src.views.perfil_view import PerfilView

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
api_alimentos = FatSecretAPI()

def calcular_requerimientos(peso_kg, altura_cm, edad_anios, objetivo):
    try:
        peso = float(peso_kg)
        altura = float(altura_cm)
        if altura < 3.0:
            altura = altura * 100
        edad = int(edad_anios)
    except:
        return 2000, 130, 220, 65 

    tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
    calorias_mantenimiento = tmb * 1.375

    if "ganar" in objetivo.lower() or "muscular" in objetivo.lower():
        calorias_objetivo = calorias_mantenimiento + 400
    elif "perder" in objetivo.lower() or "peso" in objetivo.lower():
        calorias_objetivo = calorias_mantenimiento - 400
    else:
        calorias_objetivo = calorias_mantenimiento

    proteinas = int(peso * 2)
    grasas = int(peso * 1)
    calorias_restantes = calorias_objetivo - (proteinas * 4) - (grasas * 9)
    carbohidratos = int(calorias_restantes / 4)

    return int(calorias_objetivo), proteinas, carbohidratos, grasas


def HomeView(page: ft.Page):
    user_id = page.user_data.get("id", "usuario_anonimo")
    nombre_usuario = page.user_data.get("email", "Usuario").split("@")[0].capitalize()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    peso_actual, altura_actual, edad_actual, objetivo_usuario = "64", "170", "21", "Ganar Masa Muscular"
    
    try:
        perfil = db.child("usuarios").child(user_id).child("perfil").get().val()
        if perfil:
            peso_actual = perfil.get("peso", "64")
            altura_actual = perfil.get("altura", "170")
            edad_actual = perfil.get("edad", "21")
            objetivo_usuario = perfil.get("objective", "Ganar Masa Muscular")
    except Exception as ex:
        print("Error al cargar perfil:", str(ex))

    cal_obj, prot_obj, carb_obj, gras_obj = calcular_requerimientos(
        peso_actual, altura_actual, edad_actual, objetivo_usuario
    )

    consumo_actual = {"calorias": 0, "proteinas": 0, "carbohidratos": 0, "grasas": 0, "agua": 0}

    def cargar_consumo_desde_db():
        try:
            consumo_db = db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).get().val()
            print("[DEBUG] consumo_db raw:", consumo_db)
            if consumo_db:
                # Sumar todas las comidas registradas para obtener totales fiables
                comidas = consumo_db.get("comidas", {}) or {}
                total_cal = 0.0
                total_p = 0.0
                total_c = 0.0
                total_g = 0.0
                for key, comida in (comidas.items() if isinstance(comidas, dict) else []):
                    try:
                        total_cal += float(comida.get("calorias", 0) or 0)
                    except Exception:
                        pass
                    macros = comida.get("macros", {}) or {}
                    try:
                        total_p += float(macros.get("P", 0) or 0)
                        total_c += float(macros.get("C", 0) or 0)
                        total_g += float(macros.get("G", 0) or 0)
                    except Exception:
                        pass

                consumo_actual["calorias"] = int(round(total_cal))
                consumo_actual["proteinas"] = int(round(total_p))
                consumo_actual["carbohidratos"] = int(round(total_c))
                consumo_actual["grasas"] = int(round(total_g))
                consumo_actual["agua"] = int(consumo_db.get("agua", 0) or 0)
                print("[DEBUG] consumo_actual after read:", consumo_actual)
        except Exception as ex:
            print("Error al cargar consumo diario:", str(ex))

    cargar_consumo_desde_db()

    # --- COMPONENTES DINÁMICOS DE LA PESTAÑA INICIO ---
    calorias_texto = ft.Text("", size=36, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD)
    calorias_progress = ft.ProgressBar(value=0, color="#6ee7b7", bgcolor=ft.colors.GREY_700, width=400)
    lista_comidas_view = ft.ListView(expand=True, spacing=10, padding=10)
    contenedor_historial = ft.Container(
        content=ft.Column([
            ft.Text("Comidas de hoy", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            lista_comidas_view
        ], height=250),
        bgcolor="#141720", border_radius=15, padding=15, width=450,
        border=ft.border.all(1, "rgba(255,255,255,0.04)")
    )
    agua_texto = ft.Text("", size=16, color="#38bdf8", weight=ft.FontWeight.BOLD)
    macro_cards_container = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    def eliminar_comida(key, calorias_comida, prot_comida, carb_comida, grasas_comida):
        try:
            # 1. Eliminar el registro específico de la lista de comidas
            db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).child("comidas").child(key).remove()
            
            # 2. Restar los valores de los totales globales
            nuevos_totales = {
                "calorias": consumo_actual["calorias"] - calorias_comida,
                "proteinas": consumo_actual["proteinas"] - prot_comida,
                "carbohidratos": consumo_actual["carbohidratos"] - carb_comida,
                "grasas": consumo_actual["grasas"] - grasas_comida
            }
            db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).update(nuevos_totales)
            
            # 3. Actualizar la variable local y refrescar la UI
            for k, v in nuevos_totales.items():
                consumo_actual[k] = v
            
            cargar_lista_comidas()
            construir_interfaz_inicio()
            page.update()
        except Exception as ex:
            print("Error al eliminar comida:", ex)

    def cargar_lista_comidas():
            lista_comidas_view.controls.clear()
            try:
                comidas_db = db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).child("comidas").get().val()
                if comidas_db:
                    for key, comida in comidas_db.items():
                        # Aseguramos valores por defecto si algún campo falta
                        c = comida.get('calorias', 0)
                        p = comida.get('proteinas', 0)
                        cb = comida.get('carbohidratos', 0)
                        g = comida.get('grasas', 0)
                        
                        lista_comidas_view.controls.append(
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.RESTAURANT, color="#6ee7b7"),
                                title=ft.Text(comida['nombre'], color=ft.colors.WHITE),
                                subtitle=ft.Text(f"{comida['gramos']}g | {c} kcal", color=ft.colors.GREY_400),
                                trailing=ft.IconButton(
                                    ft.icons.DELETE_OUTLINE, 
                                    icon_color=ft.colors.RED_300,
                                    # Pasamos los datos necesarios para restar correctamente
                                    on_click=lambda e, k=key, cal=c, pr=p, cr=cb, gr=g: eliminar_comida(k, cal, pr, cr, gr)
                                )
                            )
                        )
                else:
                    lista_comidas_view.controls.append(ft.Text("Aún no hay registros hoy.", color=ft.colors.GREY_600))
            except Exception as ex:
                print("Error cargando lista:", ex)
            page.update()
            
    def construir_interfaz_inicio():
        calorias_texto.value = f"{consumo_actual['calorias']} / {cal_obj} kcal"
        calorias_progress.value = consumo_actual['calorias'] / cal_obj if cal_obj > 0 else 0
        agua_texto.value = f"Agua: {consumo_actual['agua']} ml"
        
        p_prog = consumo_actual["proteinas"] / prot_obj if prot_obj > 0 else 0
        c_prog = consumo_actual["carbohidratos"] / carb_obj if carb_obj > 0 else 0
        g_prog = consumo_actual["grasas"] / gras_obj if gras_obj > 0 else 0

        macro_cards_container.controls = [
            ft.Container(content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, controls=[
                ft.Text("Proteínas", size=14, color=ft.colors.GREY_300, weight=ft.FontWeight.BOLD),
                ft.Text(f"{consumo_actual['proteinas']}g / {prot_obj}g", size=16, color=ft.colors.WHITE),
                ft.ProgressBar(value=p_prog, color="#6ee7b7", bgcolor=ft.colors.GREY_800, width=120)
            ]), bgcolor="#141720", padding=15, border_radius=10, width=140),
            ft.Container(content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, controls=[
                ft.Text("Carbohidratos", size=14, color=ft.colors.GREY_300, weight=ft.FontWeight.BOLD),
                ft.Text(f"{consumo_actual['carbohidratos']}g / {carb_obj}g", size=16, color=ft.colors.WHITE),
                ft.ProgressBar(value=c_prog, color="#38bdf8", bgcolor=ft.colors.GREY_800, width=120)
            ]), bgcolor="#141720", padding=15, border_radius=10, width=140),
            ft.Container(content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, controls=[
                ft.Text("Grasas", size=14, color=ft.colors.GREY_300, weight=ft.FontWeight.BOLD),
                ft.Text(f"{consumo_actual['grasas']}g / {gras_obj}g", size=16, color=ft.colors.WHITE),
                ft.ProgressBar(value=g_prog, color="#fbbf24", bgcolor=ft.colors.GREY_800, width=120)
            ]), bgcolor="#141720", padding=15, border_radius=10, width=140),
        ]

    construir_interfaz_inicio()

    def registrar_agua_db(e):
        consumo_actual["agua"] += 250
        try:
            db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).set(consumo_actual)
            agua_texto.value = f"Agua: {consumo_actual['agua']} ml"
            page.update()
        except Exception as ex:
            print("Error al guardar agua:", str(ex))

    # --- PESTAÑAS VISTAS ---
    calorias_card = ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Calorías Diarias", size=16, color=ft.colors.GREY_400, weight=ft.FontWeight.W_500),
                calorias_texto, calorias_progress,
                ft.Container(height=5), agua_texto
            ]
        ),
        bgcolor="#141720", padding=20, border_radius=15, width=450,
        border=ft.border.all(1, "rgba(255,255,255,0.04)")
    )

    vista_inicio = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=450,
                controls=[
                    ft.Column([
                        ft.Text(f"¡Hola, {nombre_usuario}! 👋", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"Meta: {objetivo_usuario} | {peso_actual} kg", size=14, color="#6ee7b7"),
                    ]),
                    ft.IconButton(ft.icons.LOGOUT_ROUNDED, icon_color=ft.colors.RED_ACCENT_400, on_click=lambda _: [page.user_data.clear(), page.go("/")])
                ]
            ),
            calorias_card,
            macro_cards_container,
            ft.Divider(height=10, color="rgba(255,255,255,0.05)"),
            ft.ElevatedButton(
                text="Registrar Agua (+250ml)", icon=ft.icons.WATER_DROP, 
                style=ft.ButtonStyle(bgcolor="#38bdf8", color="#0c0e16"), 
                on_click=registrar_agua_db, width=450, height=48
            ),
            contenedor_historial
        ]
    )

    # Definición completa de vista_inicio
    vista_inicio = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
        spacing=25,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                width=450,
                controls=[
                    ft.Column([
                        ft.Text(f"¡Hola, {nombre_usuario}! 👋", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text(f"Meta: {objetivo_usuario} | {peso_actual} kg", size=14, color="#6ee7b7"),
                    ]),
                    ft.IconButton(
                        ft.icons.LOGOUT_ROUNDED, 
                        icon_color=ft.colors.RED_ACCENT_400, 
                        on_click=lambda _: [page.user_data.clear(), page.go("/")]
                    )
                ]
            ),
            calorias_card,
            macro_cards_container,
            ft.Divider(height=10, color="rgba(255,255,255,0.05)"),
            ft.ElevatedButton(
                text="Registrar Agua (+250ml)", 
                icon=ft.icons.WATER_DROP, 
                style=ft.ButtonStyle(bgcolor="#38bdf8", color="#0c0e16"), 
                on_click=registrar_agua_db, 
                width=450, 
                height=48
            ),
            contenedor_historial
        ]
    )

    vista_registro = RegistroView(page) 
    vista_perfil = PerfilView(page)
    

    contenedor_central = ft.Column(controls=[vista_inicio], scroll=ft.ScrollMode.AUTO, expand=True)

    def cambiar_pestana(e):
        idx = e.control.selected_index
        
        # 1. IMPORTANTE: Limpiamos cualquier rastro de diálogos anteriores
        page.dialog = None
        
        # 2. Limpiamos el contenedor central
        contenedor_central.controls.clear()
        
        # 3. Insertamos la vista fresca
        if idx == 0:
            cargar_consumo_desde_db()
            construir_interfaz_inicio()
            contenedor_central.controls.append(vista_inicio)
        elif idx == 1:
            contenedor_central.controls.append(RegistroView(page))
        elif idx == 2:
            contenedor_central.controls.append(PerfilView(page))
        
        # 4. Una sola llamada al final
        page.update()

    cargar_lista_comidas()
    construir_interfaz_inicio()

    return ft.View(
        route="/home",
        navigation_bar=crear_navbar(page, selected_index=0),
        controls=[
            ft.Container(
                content=contenedor_central, # Ahora Python ya sabe qué es esto
                padding=20,
                expand=True
            )
        ]
    )
import os
import flet as ft
import pyrebase
import threading
from datetime import datetime
from dotenv import load_dotenv
from src.services.food_api import FatSecretAPI

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
            if consumo_db:
                consumo_actual["calorias"] = int(consumo_db.get("calorias", 0))
                consumo_actual["proteinas"] = int(consumo_db.get("proteinas", 0))
                consumo_actual["carbohidratos"] = int(consumo_db.get("carbohidratos", 0))
                consumo_actual["grasas"] = int(consumo_db.get("grasas", 0))
                consumo_actual["agua"] = int(consumo_db.get("agua", 0))
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
        
    

    # --- PESTAÑA 2: REGISTRO DE ALIMENTOS ---
    search_input = ft.TextField(
        label="Buscar alimento en internet...", expand=True,
        border_color="rgba(255,255,255,0.1)", focused_border_color="#6ee7b7"
    )
    lista_resultados = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
    indicador_carga = ft.ProgressRing(visible=False, width=22, height=22, color="#6ee7b7")

    def abrir_dialogo_porciones(food_id, food_name):
        indicador_carga.visible = True
        page.update()

        def tarea_hilo_api():
            try:
                macros = api_alimentos.obtener_macros_alimento(str(food_id))
            except Exception as ex:
                print(ex)
                macros = None

            indicador_carga.visible = False

            if not macros:
                page.snack_bar = ft.SnackBar(ft.Text("Error al obtener macros de la API."))
                page.snack_bar.open = True
                page.update()
                return

            input_gramos = ft.TextField(label="Gramos", value="100", width=120, focused_border_color="#6ee7b7")
            txt_calorias = ft.Text(f"Calorías: {macros['calorias']} kcal", weight=ft.FontWeight.BOLD, color="#6ee7b7")
            txt_p = ft.Text(f"P: {macros['proteinas']}g", color="#6ee7b7")
            txt_c = ft.Text(f"C: {macros['carbohidratos']}g", color="#38bdf8")
            txt_g = ft.Text(f"G: {macros['grasas']}g", color="#fbbf24")

            def cambiar_gramos_reactivo(e):
                try:
                    g = float(input_gramos.value) if input_gramos.value else 0.0
                    f = g / 100.0
                    txt_calorias.value = f"Calorías: {round(macros['calorias']*f, 1)} kcal"
                    txt_p.value = f"P: {round(macros['proteinas']*f, 1)}g"
                    txt_c.value = f"C: {round(macros['carbohidratos']*f, 1)}g"
                    txt_g.value = f"G: {round(macros['grasas']*f, 1)}g"
                    page.update()
                except:
                    pass

            input_gramos.on_change = cambiar_gramos_reactivo

            # Declaramos la referencia del diálogo vacía primero para usarla internamente
            dialogo_gramos = None

            def cerrar_dialogo_seguro(e):
                dialogo_gramos.open = False
                page.update()

            def confirmar_adicion(e):
                try:
                    g_finales = float(input_gramos.value)
                    f = g_finales / 100.0
                    
                    # 1. Crear el objeto de la nueva comida
                    nueva_comida = {
                        "nombre": food_name,
                        "gramos": g_finales,
                        "calorias": int(macros["calorias"] * f)
                    }
                    
                    # 2. Guardar la comida en el nodo "comidas"
                    db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).child("comidas").push(nueva_comida)
                    
                    # 3. Actualizar los totales (usando update para no borrar lo anterior)
                    nuevos_totales = {
                        "calorias": consumo_actual["calorias"] + int(macros["calorias"] * f),
                        "proteinas": consumo_actual["proteinas"] + int(macros["proteinas"] * f),
                        "carbohidratos": consumo_actual["carbohidratos"] + int(macros["carbohidratos"] * f),
                        "grasas": consumo_actual["grasas"] + int(macros["grasas"] * f)
                    }
                    db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).update(nuevos_totales)
                    
                    # Actualizar consumo_actual local para que la UI refleje el cambio
                    for k, v in nuevos_totales.items():
                        consumo_actual[k] = v

                    dialogo_gramos.open = False
                    cargar_lista_comidas() # <-- Recarga la lista
                    construir_interfaz_inicio() # <-- Actualiza los progresos
                    page.update()
                except Exception as err:
                    print("Error al guardar:", err)

            dialogo_gramos = ft.AlertDialog(
                title=ft.Text(f"Añadir {macros['nombre']}"),
                content=ft.Column([
                    ft.Text(f"Base: {macros['porcion_texto']}", italic=True, size=12, color=ft.colors.GREY_400),
                    ft.Row([input_gramos, ft.Text("g", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(color="rgba(255,255,255,0.1)"),
                    txt_calorias,
                    ft.Row([txt_p, txt_c, txt_g], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], tight=True, spacing=12),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_dialogo_seguro),
                    ft.ElevatedButton("Agregar", bgcolor="#6ee7b7", color="#0c0e16", on_click=confirmar_adicion)
                ]
            )
            
            # Asignamos al diálogo de la página de manera limpia
            page.dialog = dialogo_gramos
            dialogo_gramos.open = True
            page.update()

        threading.Thread(target=tarea_hilo_api).start()

    def ejecutar_busqueda(e):
        if not search_input.value.strip(): return
        indicador_carga.visible = True
        lista_resultados.controls.clear()
        page.update()

        def thread_buscar():
            productos = api_alimentos.buscar_alimento(search_input.value)
            indicador_carga.visible = False
            if not productos:
                lista_resultados.controls.append(ft.Text("No se encontraron alimentos.", color="#fbbf24", text_align=ft.TextAlign.CENTER))
            else:
                for p in productos:
                    lista_resultados.controls.append(
                        ft.Container(
                            content=ft.ListTile(
                                title=ft.Text(p["nombre"], weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"{p['marca']} - {p['descripcion']}", size=11, color=ft.colors.GREY_400),
                                trailing=ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, icon_color="#6ee7b7", on_click=lambda _, fid=p["id"], fname=p["nombre"]: abrir_dialogo_porciones(fid, fname))
                            ),
                            bgcolor="#141720", border_radius=12, padding=2,
                            border=ft.border.all(1, "rgba(255,255,255,0.03)")
                        )
                    )
            page.update()
            
        threading.Thread(target=thread_buscar).start()

    vista_registro = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15,
        controls=[
            ft.Text("Registro de Comidas", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Row([search_input, ft.IconButton(ft.icons.SEARCH, icon_color="#6ee7b7", height=48, on_click=ejecutar_busqueda), indicador_carga], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color="rgba(255,255,255,0.05)"),
            lista_resultados
        ]
    )

    # --- PESTAÑA 3: PERFIL ---
    vista_perfil = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
        controls=[
            ft.Text("Mi Perfil", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Container(
                content=ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.icons.PERSON, color="#6ee7b7"), title=ft.Text("Usuario"), subtitle=ft.Text(nombre_usuario)),
                    ft.ListTile(leading=ft.Icon(ft.icons.FITNESS_CENTER, color="#38bdf8"), title=ft.Text("Meta Actual"), subtitle=ft.Text(objetivo_usuario)),
                    ft.ListTile(leading=ft.Icon(ft.icons.SPEED, color="#fbbf24"), title=ft.Text("Peso registrado"), subtitle=ft.Text(f"{peso_actual} kg - {altura_actual} cm")),
                ]),
                bgcolor="#141720", padding=10, border_radius=15, width=450,
                border=ft.border.all(1, "rgba(255,255,255,0.04)")
            )
        ]
    )

    # --- NAVEGACIÓN ---
    contenedor_central = ft.Column(controls=[vista_inicio], scroll=ft.ScrollMode.AUTO, expand=True)

    def cambiar_pestana(e):
        idx = e.control.selected_index
        contenedor_central.controls.clear()
        
        if idx == 0:
            cargar_consumo_desde_db()
            construir_interfaz_inicio()
            contenedor_central.controls.append(vista_inicio)
        elif idx == 1:
            contenedor_central.controls.append(vista_registro)
        elif idx == 2:
            contenedor_central.controls.append(vista_perfil)
        
        page.update()

    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor="#0c0e16",
        on_change=cambiar_pestana,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.HOME_ROUNDED, label="Inicio"),
            ft.NavigationDestination(icon=ft.icons.FASTFOOD_ROUNDED, label="Registrar"),
            ft.NavigationDestination(icon=ft.icons.ACCOUNT_CIRCLE_ROUNDED, label="Perfil"),
        ]
    )

    cargar_lista_comidas()

    return ft.View(
        route="/home",
        navigation_bar=nav_bar,
        controls=[
            ft.Container(
                content=contenedor_central,
                padding=20,
                expand=True
            )
        ]
    )
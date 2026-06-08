import flet as ft
import threading
from src.services.food_api import FatSecretAPI
from src.services.firebase_db import db
from datetime import datetime
import re

api_alimentos = FatSecretAPI()

def RegistroView(page: ft.Page):
    user_id = page.user_data.get("id")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    estado = {"lista_cache": []}
    filtros_inteligentes = {
        "Snacks": "yogurt natural almendras fruta",
        "Proteínas": "pechuga pollo huevo entero carne magra", # "Pechuga" y "entero" filtran mucho mejor
        "Carbos": "arroz blanco avena integral papa",
        "Grasas": "aceite oliva aguacate natural"
    }

    def abrir_modal(nombre, desc):
        # --- EXTRACCIÓN DE DATOS DE LA DESCRIPCIÓN ---
        # "Por 100g - Calorías: 147kcal | Grasas: 9,94g | Carbohidratos: 0,77g | Proteínas: 12,58g"
        def parse_num(x):
            if x is None:
                return 0.0
            if isinstance(x, (int, float)):
                return float(x)
            s = str(x).replace(',', '.').strip()
            m = re.search(r"-?\d+(?:\.\d+)?", s)
            return float(m.group(0)) if m else 0.0

        try:
            base = desc.split(" - ")[0]
            cal_str = desc.split("Calorías: ")[1].split("kcal")[0]
            grasas_str = desc.split("Grasas: ")[1].split("g")[0]
            carbos_str = desc.split("Carbohidratos: ")[1].split("g")[0]
            proteinas_str = desc.split("Proteínas: ")[1].split("g")[0]
        except Exception:
            base, cal_str, grasas_str, carbos_str, proteinas_str = "100g", "0", "0", "0", "0"

        # Valores numéricos seguros (usar en cálculos)
        cal_val = parse_num(cal_str)
        grasas_val = parse_num(grasas_str)
        carbos_val = parse_num(carbos_str)
        proteinas_val = parse_num(proteinas_str)

        gramos_input = ft.TextField(
            value="100",
            width=80,
            text_align=ft.TextAlign.CENTER,
            border_color="white24",
            focused_border_color="#6ee7b7",
            keyboard_type=ft.KeyboardType.NUMBER
        )

        def guardar(e):
            # Verificar que hay un usuario logueado
            if not user_id:
                page.snack_bar = ft.SnackBar(ft.Text("No has iniciado sesión."), open=True)
                page.update()
                return

            # Lógica para calcular calorías según gramos ingresados (usa valores seguros)
            try:
                gramos = float(str(gramos_input.value).replace(',', '.'))
            except Exception:
                gramos = 100.0
            factor = gramos / 100.0
            data = {
                "nombre": nombre,
                "calorias": round(cal_val * factor, 2),
                "gramos": str(int(gramos)) if gramos.is_integer() else str(gramos),
                "macros": {
                    "P": round(proteinas_val * factor, 2),
                    "C": round(carbos_val * factor, 2),
                    "G": round(grasas_val * factor, 2)
                },
                "fecha": fecha_hoy
            }
            # Guardar comida
            comidas_ref = db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy)
            comidas_ref.child("comidas").push(data)

            # Actualizar totales diarios sumando la nueva comida
            try:
                consumo_actual_db = comidas_ref.get().val() or {}
                # Valores existentes (aseguramos numéricos)
                prev_cal = float(consumo_actual_db.get("calorias", 0) or 0)
                prev_p = float(consumo_actual_db.get("proteinas", 0) or 0)
                prev_c = float(consumo_actual_db.get("carbohidratos", 0) or 0)
                prev_g = float(consumo_actual_db.get("grasas", 0) or 0)

                nuevos = {
                    "calorias": round(prev_cal + data["calorias"], 2),
                    "proteinas": round(prev_p + data["macros"]["P"], 2),
                    "carbohidratos": round(prev_c + data["macros"]["C"], 2),
                    "grasas": round(prev_g + data["macros"]["G"], 2)
                }
                comidas_ref.update(nuevos)
            except Exception as ex:
                print("Error actualizando totales diarios:", ex)
            # Lectura de verificación y notificación al usuario
            try:
                snapshot = comidas_ref.get().val()
                print("[DB DEBUG] consumo_diario after write:", snapshot)
                page.snack_bar = ft.SnackBar(ft.Text("Comida añadida correctamente."), open=True)
            except Exception as ex:
                print("[DB DEBUG] error leyendo después de escribir:", ex)
                page.snack_bar = ft.SnackBar(ft.Text("La comida pudo no haberse guardado."), open=True)
            page.update()
            page.dialog.open = False

        # --- DISEÑO DE LA VENTANA ---
        page.dialog = ft.AlertDialog(
            bgcolor="#141720",
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
                width=300,
                padding=10,
                content=ft.Column([
                    ft.Text(f"Añadir {nombre}", size=18, weight="bold"),
                    ft.Text(f"Base: {base}", size=12, color="white60"),
                    ft.Divider(height=10, color="transparent"),
                    
                    # Selector de Gramos
                    ft.Row([
                        ft.Column([
                            ft.Text("Gramos", size=12, color="white60"),
                            gramos_input,
                        ], horizontal_alignment="center"),
                        ft.Text("g", size=20, weight="bold")
                    ], alignment="center", spacing=10),
                    
                    ft.Divider(height=20, color="transparent"),
                    
                    # Info Nutricional con colores
                    ft.Text(f"Calorías: {round(cal_val,2)} kcal", color="#6ee7b7", weight="bold", size=16),
                    ft.Row([
                        ft.Text(f"P: {round(proteinas_val,2)}g", color="#6ee7b7", weight="bold"),
                        ft.Text(f"C: {round(carbos_val,2)}g", color="#4fc3f7", weight="bold"),
                        ft.Text(f"G: {round(grasas_val,2)}g", color="#ffd54f", weight="bold"),
                    ], alignment="spaceBetween"),
                    
                    ft.Divider(height=10, color="transparent"),
                    
                    # Botones
                    ft.Row([
                        ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                        ft.ElevatedButton(
                            "Agregar", 
                            bgcolor="#6ee7b7", 
                            color="black",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=guardar
                        )
                    ], alignment="end")
                ], tight=True, horizontal_alignment="center")
            )
        )
        page.dialog.open = True
        page.update()

    def thread_buscar():
        estado["lista_cache"] = api_alimentos.buscar_alimento(search_input.value)
        indicador_carga.visible = False
        for p in estado["lista_cache"]:
            nombre = p.get("nombre")
            desc = p.get("descripcion") # Pasamos la descripción completa
            lista_resultados.controls.append(
                ft.ListTile(
                    title=ft.Text(nombre, weight="bold"),
                    subtitle=ft.Text(desc, size=12),
                    trailing=ft.IconButton(
                        ft.icons.ADD_CIRCLE, 
                        icon_color="#6ee7b7",
                        on_click=lambda e, n=nombre, d=desc: abrir_modal(n, d)
                    )
                )
            )
        page.update()

    # --- El resto del Layout del RegistroView se mantiene igual ---
    search_input = ft.TextField(label="Buscar alimento...", expand=True)
    lista_resultados = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    indicador_carga = ft.ProgressRing(visible=False)

    def ejecutar_busqueda(e):
        if not search_input.value.strip(): return
        indicador_carga.visible = True
        lista_resultados.controls.clear()
        threading.Thread(target=thread_buscar).start()
        page.update()

    def aplicar_filtro(e):
        categoria = e.control.text
        
        if categoria != "Todos" and categoria in filtros_inteligentes:
            search_input.value = filtros_inteligentes[categoria]
            indicador_carga.visible = True
            page.update()
            # Actualizamos la caché con la nueva categoría
            estado["lista_cache"] = api_alimentos.buscar_alimento(search_input.value)
            indicador_carga.visible = False
        
        lista_resultados.controls.clear()
        for p in estado["lista_cache"]:
            # Filtramos comparando contra la descripción
            if categoria == "Todos" or categoria.lower() in p.get("descripcion", "").lower():
                nombre = p.get("nombre")
                desc = p.get("descripcion")
                # Usamos el mismo diseño de ListTile que en la búsqueda normal
                lista_resultados.controls.append(
                    ft.ListTile(
                        title=ft.Text(nombre, weight="bold"),
                        subtitle=ft.Text(desc, size=12),
                        trailing=ft.IconButton(
                            ft.icons.ADD_CIRCLE, 
                            icon_color="#6ee7b7",
                            on_click=lambda e, n=nombre, d=desc: abrir_modal(n, d)
                        )
                    )
                )
        page.update()

    return ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Registrar Comida", size=22, weight="bold"),
                ft.Row([
                    search_input, 
                    ft.IconButton(ft.icons.SEARCH, on_click=ejecutar_busqueda)
                ]),
                ft.Row([
                    ft.ElevatedButton("Todos", on_click=aplicar_filtro),
                    ft.ElevatedButton("Snacks", on_click=aplicar_filtro),
                    ft.ElevatedButton("Proteínas", on_click=aplicar_filtro),
                    ft.ElevatedButton("Carbos", on_click=aplicar_filtro),
                    ft.ElevatedButton("Grasas", on_click=aplicar_filtro)
                ], scroll=ft.ScrollMode.AUTO),
                indicador_carga,
                lista_resultados
            ], 
            
        )
    )
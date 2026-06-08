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

    # Recetas favoritas del usuario (se muestran en esta pestaña)
    recetas_fav_db = []
    # Favoritas: fixed-width card to avoid forcing the parent column to expand
    fav_container = ft.Container(content=ft.Column([], spacing=8), bgcolor="#141720", padding=12, border_radius=12, width=450, border=ft.border.all(1, "rgba(255,255,255,0.04)"))

    def cargar_favoritas():
        nonlocal recetas_fav_db
        recetas_fav_db = []
        try:
            favs = db.child("usuarios").child(user_id).child("recetas_favoritas").get().val() or {}
            for k, v in favs.items():
                recetas_fav_db.append((k, v))
        except Exception as ex:
            print("Error cargando favoritas:", ex)

        # Construir controles para el contenedor
        fav_controls = []
        if recetas_fav_db:
            for key, receta in recetas_fav_db:
                # Normalizar texto (eliminar saltos de línea o estructura inesperada)
                raw_titulo = receta.get("titulo") or receta.get("nombre") or "Receta"
                titulo = " ".join(str(raw_titulo).replace('\r', ' ').replace('\n', ' ').split())
                raw_desc = receta.get("desc", "")
                desc = " ".join(str(raw_desc).replace('\r', ' ').replace('\n', ' ').split())

                def reg_from_fav(e, receta=receta):
                    g = 250
                    cal = receta.get("calorias", 0)
                    macros = receta.get("macros", {}) or {}
                    factor = g / 100.0 if g and cal else (g / 100.0 if g else 0)
                    datos = {
                        "nombre": receta.get("titulo", receta.get("nombre")),
                        "gramos": g,
                        "calorias": int(round(cal * factor)) if cal else 0,
                        "proteinas": int(round(macros.get("P", 0) * factor)) if macros else 0,
                        "carbohidratos": int(round(macros.get("C", 0) * factor)) if macros else 0,
                        "grasas": int(round(macros.get("G", 0) * factor)) if macros else 0,
                        "origen": "favorita",
                        "fecha": fecha_hoy
                    }
                    try:
                        db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).child("comidas").push(datos)
                        page.snack_bar = ft.SnackBar(ft.Text("Registro agregado desde favoritas"))
                        page.snack_bar.open = True
                        page.update()
                    except Exception as ex:
                        print("Error registrando desde favorita:", ex)

                def eliminar_fav(e, key=key):
                    try:
                        db.child("usuarios").child(user_id).child("recetas_favoritas").child(key).remove()
                        cargar_favoritas()
                        page.snack_bar = ft.SnackBar(ft.Text("Favorita eliminada"))
                        page.snack_bar.open = True
                        page.update()
                    except Exception as ex:
                        print("Error eliminando favorita:", ex)

                # Use a responsive Row so title doesn't get forced to a tiny column
                fav_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(ft.Icon(ft.icons.RESTAURANT, color="#6ee7b7"), padding=8),
                            ft.Column([ft.Text(titulo, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD), ft.Text(desc, color=ft.colors.GREY_400)], expand=True),
                            ft.Row([ft.ElevatedButton("Registrar", on_click=reg_from_fav, height=36), ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_300, on_click=eliminar_fav)], spacing=6)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=8, border_radius=8, bgcolor="#0f1114"
                    )
                )

        if fav_controls:
            fav_container.content = ft.Column([ft.Text("Recetas Favoritas", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)] + fav_controls, spacing=8)
        else:
            fav_container.content = ft.Column([ft.Text("Recetas Favoritas", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text("Aún no hay recetas favoritas.", color=ft.colors.GREY_600)], spacing=8)

    # cargar inicialmente
    try:
        cargar_favoritas()
    except Exception:
        pass

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
                page.snack_bar = ft.SnackBar(ft.Text("Comida añadida correctamente."), open=True)
            except Exception:
                page.snack_bar = ft.SnackBar(ft.Text("La comida pudo no haberse guardado."), open=True)
            page.update()
            page.dialog.open = False

        # --- DISEÑO DE LA VENTANA ---
        # Dialog ajustable al contenido (sin ancho fijo)
        page.dialog = ft.AlertDialog(
            bgcolor="#141720",
            shape=ft.RoundedRectangleBorder(radius=20),
            content=ft.Container(
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
        # Enriquecer query con preferencias del perfil (si existen)
        try:
            perfil = db.child("usuarios").child(user_id).child("perfil").get().val() or {}
            prefs = perfil.get("preferencias", {}) or {}
        except Exception:
            prefs = {}

        q = search_input.value or ""
        pref_map = {
            "vegetariano": "vegetariano",
            "vegano": "vegano",
            "pescatariano": "pescatariano",
            "sin_lactosa": "sin lactosa",
            "sin_gluten": "sin gluten",
            "sin_frutos_secos": "sin frutos secos",
            "bajo_sodio": "bajo sodio",
            "bajo_azucar": "bajo en azúcar",
            "alta_proteina": "alta proteína"
        }
        for k, v in prefs.items():
            if v and k in pref_map:
                q = f"{q} {pref_map[k]}" if q else pref_map[k]

        estado["lista_cache"] = api_alimentos.buscar_alimento(q)
        indicador_carga.visible = False
        for p in estado["lista_cache"]:
            nombre = p.get("nombre")
            desc = p.get("descripcion") # Pasamos la descripción completa
            # Filtrado por preferencias: excluir si contradice (p. ej. vegetariano vs carne)
            desc_l = (desc or "").lower()
            skip = False
            # reglas simples de exclusión
            if prefs.get("vegetariano"):
                for w in ["pollo","carne","res","cerdo","jamon","bacon","salchicha","pescado"]:
                    if w in desc_l:
                        skip = True
                        break
            if prefs.get("vegano"):
                for w in ["huevo","leche","queso","miel","yogurt","mantequilla"]:
                    if w in desc_l:
                        skip = True
                        break
            if prefs.get("sin_lactosa"):
                for w in ["leche","lacte","queso","yogurt"]:
                    if w in desc_l:
                        skip = True
                        break
            if prefs.get("sin_frutos_secos"):
                for w in ["almendra","nuez","cacahu","pistacho","avellana"]:
                    if w in desc_l:
                        skip = True
                        break
            if prefs.get("sin_gluten"):
                for w in ["trigo","pan","pasta","harina","galleta"]:
                    if w in desc_l:
                        skip = True
                        break

            if skip:
                continue

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
    # No usar ListView/scroll interno aquí: dejar que el contenedor padre gestione el scroll
    lista_resultados = ft.Column()
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
                lista_resultados,
                ft.Container(height=12),
                fav_container
            ], 
            
        )
    )
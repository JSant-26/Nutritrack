import flet as ft
from src.services.firebase_db import db
from datetime import datetime
from src.styles.styles import card_container, header_text, small_text, BG, ACCENT, CARD_BG, fancy_card


def PlanView(page: ft.Page):
    user_id = page.user_data.get("id")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    # Cargar perfil básico si existe
    perfil = {}
    try:
        if user_id:
            perfil = db.child("usuarios").child(user_id).child("perfil").get().val() or {}
    except Exception:
        perfil = {}

    objetivo = perfil.get("objective") or perfil.get("objetivo") or "Sin objetivo definido"
    peso = perfil.get("peso", "--")
    altura = perfil.get("altura", "--")

    # Tarjeta 1: Objetivo actual
    # Calcular requerimientos con la misma lógica que Home
    from src.utils.nutrition import calcular_requerimientos
    cal_obj, prot_obj, carb_obj, gras_obj = calcular_requerimientos(peso, altura, perfil.get("edad", 21), objetivo)

    # Card con gradiente y resumen de macros
    # Primera tarjeta con icono y macros (iconos añadidos para mayor claridad)
    objetivo_card = fancy_card(
        ft.Column([
            ft.Row([
                ft.Container(ft.Icon(ft.icons.FITNESS_CENTER, size=36, color=ACCENT), padding=10, border_radius=12, bgcolor="#071018"),
                ft.Column([
                    ft.Text("Objetivo Actual", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Text(f"{objetivo}", color=ft.colors.WHITE),
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.START, spacing=12),
            ft.Divider(height=10, color="transparent"),
            ft.Text(f"Peso: {peso} kg | Altura: {altura} cm", color=ft.colors.WHITE60),
            ft.Container(height=6),
            ft.Row([
                ft.Column([ft.Icon(ft.icons.FLASH_ON, size=18, color=ACCENT), ft.Text(f"{cal_obj} kcal", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text("Meta", size=12, color=ft.colors.WHITE60)], spacing=4),
                ft.Column([ft.Icon(ft.icons.FITNESS_CENTER, size=18, color=ACCENT), ft.Text(f"{prot_obj}g", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text("Proteínas", size=12, color=ft.colors.WHITE60)], spacing=4),
                ft.Column([ft.Icon(ft.icons.BAR_CHART, size=18, color=ACCENT), ft.Text(f"{carb_obj}g", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text("Carbos", size=12, color=ft.colors.WHITE60)], spacing=4),
                ft.Column([ft.Icon(ft.icons.RESTAURANT, size=18, color=ACCENT), ft.Text(f"{gras_obj}g", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text("Grasas", size=12, color=ft.colors.WHITE60)], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        ]), colors=("#0f1724", "#071018")
    )

    # Generación dinámica de recetas según objetivo
    def get_recipes_for_objective(obj):
        o = (obj or "").lower()
        # Ejemplos simples — pueden sustituirse por llamadas a API/DB
        high_protein = [
            {"titulo": "Pechuga de pollo a la plancha", "desc": "Rica en proteínas, baja en grasas.", "ingredientes": ["200g pechuga de pollo", "sal y pimienta", "1 cda aceite de oliva"], "preparacion": "Sazona la pechuga y cocina a la plancha 6-8 min por lado.", "calorias": 220, "macros": {"P": 40, "C": 0, "G": 5}},
            {"titulo": "Tazón de garbanzos y atún", "desc": "Proteínas y carbohidratos complejos.", "ingredientes": ["150g garbanzos cocidos", "100g atún", "verduras al gusto"], "preparacion": "Mezcla garbanzos con atún y verduras; aliña al gusto.", "calorias": 340, "macros": {"P": 25, "C": 35, "G": 8}},
            {"titulo": "Batido proteico verde", "desc": "Proteínas y micronutrientes.", "ingredientes": ["1 scoop proteína", "200ml leche vegetal", "1 puñado espinacas", "1/2 plátano"], "preparacion": "Licuar todos los ingredientes hasta homogeneizar.", "calorias": 280, "macros": {"P": 25, "C": 30, "G": 6}}
        ]
        fat_loss = [
            {"titulo": "Ensalada de salmón y espinacas", "desc": "Alta en omega-3 y baja en calorías.", "ingredientes": ["100g salmón", "espinacas", "limón"], "preparacion": "Combina salmón con espinacas y aliña.", "calorias": 300, "macros": {"P": 22, "C": 5, "G": 18}},
            {"titulo": "Sopa de verduras ligera", "desc": "Baja densidad calórica, saciante.", "ingredientes": ["varias verduras", "caldo vegetal"], "preparacion": "Cuece verduras en caldo y sirve caliente.", "calorias": 120, "macros": {"P": 4, "C": 20, "G": 2}},
            {"titulo": "Pechuga de pollo asada", "desc": "Proteína magra para mantener masa muscular.", "ingredientes": ["200g pechuga de pollo", "hierbas"], "preparacion": "Hornea la pechuga hasta que esté cocida.", "calorias": 220, "macros": {"P": 40, "C": 0, "G": 5}}
        ]
        balanced = [
            {"titulo": "Quinoa con verduras asadas", "desc": "Carbohidratos complejos y fibra.", "ingredientes": ["100g quinoa", "verduras"], "preparacion": "Asa verduras y mezcla con quinoa cocida.", "calorias": 360, "macros": {"P": 10, "C": 50, "G": 8}},
            {"titulo": "Tortilla de claras con espinacas", "desc": "Proteínas y vegetales.", "ingredientes": ["4 claras", "espinacas"], "preparacion": "Bate claras y cocina con espinacas.", "calorias": 140, "macros": {"P": 25, "C": 2, "G": 3}},
            {"titulo": "Filete de pescado con arroz integral", "desc": "Balance de macros.", "ingredientes": ["150g pescado", "100g arroz integral"], "preparacion": "Cocina pescado y sirve con arroz.", "calorias": 420, "macros": {"P": 30, "C": 50, "G": 10}}
        ]

        if "ganar" in o or "muscular" in o or "masa" in o:
            return high_protein
        if "perder" in o or "peso" in o or "defin" in o:
            return fat_loss
        return balanced

    recetas = get_recipes_for_objective(objetivo)
    # Rotar recetas diariamente para variar la sugerencia
    try:
        fecha_obj = datetime.now()
        day_index = fecha_obj.day - 1
        if recetas:
            start = day_index % len(recetas)
            rotated = recetas[start:] + recetas[:start]
        else:
            rotated = recetas
    except Exception:
        rotated = recetas

    # Recetas como pequeñas tarjetas con icono (mostrar hasta 3 por día)
    recetas_rows = []
    for rec in rotated[:3]:
        # Handlers for dialog actions
        def abrir_info(e, receta=rec):
            ingredientes = receta.get("ingredientes", [])
            preparacion = receta.get("preparacion", "")

            content = ft.Column([
                ft.Text(receta["titulo"], weight=ft.FontWeight.BOLD, size=16, color=ft.colors.WHITE),
                ft.Divider(height=8, color="transparent"),
                ft.Text(receta.get("desc", ""), color=ft.colors.GREY_400),
                ft.Divider(height=6, color="transparent"),
                ft.Text("Ingredientes:", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Column([ft.Text(f"- {ing}", color=ft.colors.GREY_300) for ing in ingredientes], spacing=4),
                ft.Divider(height=6, color="transparent"),
                ft.Text("Preparación:", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text(preparacion, color=ft.colors.GREY_300)
            ], tight=True)

            def _registrar(e):
                page.dialog.open = False
                page.update()
                registrar_receta(None, receta)

            def _fav(e):
                page.dialog.open = False
                page.update()
                agregar_favorita(None, receta)

            page.dialog = ft.AlertDialog(content=ft.Container(content=content, padding=10), actions=[ft.TextButton("Cerrar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update())), ft.ElevatedButton("Registrar", on_click=_registrar), ft.OutlinedButton("Guardar en favoritas", on_click=_fav)])
            page.dialog.open = True
            page.update()

        def registrar_receta(e, receta=rec):
            # Pedir gramos al usuario antes de registrar
            gramos_field = ft.TextField(value="250", label="Gramos", width=120)

            def confirmar_registro(evt):
                try:
                    g = float(gramos_field.value or 0)
                except Exception:
                    g = 0
                # Estimar calorías y macros proporcionalmente si receta tiene datos
                cal = receta.get("calorias", 0)
                macros = receta.get("macros", {}) or {}
                factor = g / 100.0 if g and cal else (g / 100.0 if g else 0)
                datos = {
                    "nombre": receta.get("titulo"),
                    "gramos": g,
                    "calorias": int(round(cal * factor)) if cal else 0,
                    "proteinas": int(round(macros.get("P", 0) * factor)) if macros else 0,
                    "carbohidratos": int(round(macros.get("C", 0) * factor)) if macros else 0,
                    "grasas": int(round(macros.get("G", 0) * factor)) if macros else 0,
                    "origen": "receta"
                }
                try:
                    db.child("usuarios").child(user_id).child("consumo_diario").child(fecha_hoy).child("comidas").push(datos)
                except Exception as ex:
                    print("Error registrando receta:", ex)
                page.dialog.open = False
                page.update()

            page.dialog = ft.AlertDialog(content=ft.Column([ft.Text("Registrar receta"), gramos_field], tight=True), actions=[ft.TextButton("Cancelar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update())), ft.ElevatedButton("Confirmar", on_click=confirmar_registro)])
            page.dialog.open = True
            page.update()

        def agregar_favorita(e, receta=rec):
            try:
                db.child("usuarios").child(user_id).child("recetas_favoritas").push(receta)
            except Exception as ex:
                print("Error guardando favorita:", ex)
            # Proveer feedback
            page.snack_bar = ft.SnackBar(ft.Text("Receta guardada en favoritas"))
            page.snack_bar.open = True
            page.update()

        recetas_rows.append(
            fancy_card(
                ft.Row([
                    ft.Container(ft.Icon(ft.icons.RESTAURANT_MENU, size=28, color=ACCENT), padding=8, border_radius=8, bgcolor="#071018"),
                    ft.Column([ft.Text(rec["titulo"], weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text(rec["desc"], size=12, color=ft.colors.GREY_400)]),
                    ft.Row([ft.IconButton(ft.icons.INFO_OUTLINE, icon_color=ft.colors.BLUE_300, on_click=abrir_info), ft.ElevatedButton("Registrar", on_click=lambda e, r=rec: registrar_receta(e, r)), ft.OutlinedButton("Favorito", on_click=lambda e, r=rec: agregar_favorita(e, r))], spacing=6)
                ], spacing=12), colors=("#071018", "#0f1114"), height=72
            )
        )

    recetas_card = card_container(
        ft.Column([
            header_text("Recetas Sugeridas"),
            ft.Divider(height=6, color="transparent"),
            ft.Column(recetas_rows, spacing=8)
        ])
    )

    # Tarjeta 3: Recomendaciones semanales (placeholder)
    # Lista más amplia de recomendaciones — se seleccionan semanalmente
    recomendaciones_all = [
        "Incluye verduras en al menos 2 comidas al día.",
        "Distribuye proteínas en las 3 comidas principales.",
        "Planifica una comida alta en carbohidratos antes de entrenar.",
        "Mantén una hidratación constante a lo largo del día.",
        "Evita bebidas azucaradas y prioriza agua o infusiones.",
        "Integra una porción de grasas saludables en una comida.",
        "Realiza un snack proteico si entrenas intensamente.",
        "Prefiere carbohidratos complejos en la cena si buscas recuperación.",
    ]
    try:
        week_number = datetime.now().isocalendar()[1]
        start_w = week_number % len(recomendaciones_all)
        weekly = recomendaciones_all[start_w:] + recomendaciones_all[:start_w]
    except Exception:
        weekly = recomendaciones_all

    recom_list = ft.Column([ft.Text(f"• {r}", color=ft.colors.GREY_300) for r in weekly[:3]], spacing=6)
    recom_card = card_container(
        ft.Column([
            header_text("Recomendaciones Semana"),
            ft.Divider(height=6, color="transparent"),
            recom_list
        ])
    )

    contenido = ft.Column([
        objetivo_card,
        ft.Container(height=12),
        recetas_card,
        ft.Container(height=12),
        recom_card
    ], spacing=10)

    # Devolver un contenedor simple (el ft.View exterior gestiona el scroll)
    return ft.Container(
        padding=20,
        content=contenido
    )

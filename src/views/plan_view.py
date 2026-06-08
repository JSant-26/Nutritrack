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
            {"titulo": "Pechuga de pollo a la plancha", "desc": "Rica en proteínas, baja en grasas."},
            {"titulo": "Tazón de garbanzos y atún", "desc": "Proteínas y carbohidratos complejos."},
            {"titulo": "Batido proteico verde", "desc": "Proteínas y micronutrientes."}
        ]
        fat_loss = [
            {"titulo": "Ensalada de salmón y espinacas", "desc": "Alta en omega-3 y baja en calorías."},
            {"titulo": "Sopa de verduras ligera", "desc": "Baja densidad calórica, saciante."},
            {"titulo": "Pechuga de pollo asada", "desc": "Proteína magra para mantener masa muscular."}
        ]
        balanced = [
            {"titulo": "Quinoa con verduras asadas", "desc": "Carbohidratos complejos y fibra."},
            {"titulo": "Tortilla de claras con espinacas", "desc": "Proteínas y vegetales."},
            {"titulo": "Filete de pescado con arroz integral", "desc": "Balance de macros."}
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
        recetas_rows.append(
            fancy_card(
                ft.Row([
                    ft.Container(ft.Icon(ft.icons.RESTAURANT_MENU, size=28, color=ACCENT), padding=8, border_radius=8, bgcolor="#071018"),
                    ft.Column([ft.Text(rec["titulo"], weight=ft.FontWeight.BOLD, color=ft.colors.WHITE), ft.Text(rec["desc"], size=12, color=ft.colors.GREY_400)])
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

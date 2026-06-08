import flet as ft
from src.services.firebase_db import db
from datetime import datetime, timedelta
from src.utils.nutrition import calcular_requerimientos
from src.styles import styles

def PerfilView(page: ft.Page):
    user_id = page.user_data.get("id")
    user_email = page.user_data.get("email", "Usuario")

    perfil = {}
    try:
        if user_id:
            perfil = db.child("usuarios").child(user_id).child("perfil").get().val() or {}
    except Exception:
        perfil = {}

    peso_val = perfil.get("peso", "")
    altura_val = perfil.get("altura", "")
    edad_val = perfil.get("edad", "")
    objetivo_val = perfil.get("objetivo", perfil.get("objective", ""))

    peso_field = ft.TextField(label="Peso (kg)", hint_text="Ej: 70", width=300, value=str(peso_val), border_color="rgba(255,255,255,0.06)", focused_border_color=styles.ACCENT)
    altura_field = ft.TextField(label="Altura (cm)", hint_text="Ej: 175", width=300, value=str(altura_val), border_color="rgba(255,255,255,0.06)", focused_border_color=styles.ACCENT)
    edad_field = ft.TextField(label="Edad", hint_text="Ej: 25", width=300, value=str(edad_val), border_color="rgba(255,255,255,0.06)", focused_border_color=styles.ACCENT)
    # objetivo and meta_peso are managed from the menu card (third card)

    def guardar_perfil(e):
        if not user_id:
            page.snack_bar = ft.SnackBar(ft.Text("No has iniciado sesión."), open=True)
            page.update()
            return
        datos = {
            "peso": peso_field.value or "",
            "altura": altura_field.value or "",
            "edad": edad_field.value or "",
            # objetivo/meta_peso kept from perfil (managed in menu card)
            "objetivo": perfil.get("objetivo", objetivo_val or ""),
            "meta_peso": perfil.get("meta_peso", "")
        }
        try:
            db.child("usuarios").child(user_id).child("perfil").set(datos)
            # Guardar snapshot histórico de peso para permitir resúmenes mensuales
            try:
                peso_val = float(str(datos.get("peso", "")).replace(",", "."))
                fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                db.child("usuarios").child(user_id).child("peso_historial").child(fecha_hoy).set(peso_val)
            except Exception:
                pass
            # update local cache and refresh resumen
            perfil.update(datos)
            page.snack_bar = ft.SnackBar(ft.Text("Perfil guardado."), open=True)
            try:
                calcular_resumen_mensual()
            except Exception:
                pass
            page.update()
        except Exception as ex:
            print("Error guardando perfil:", ex)
            page.snack_bar = ft.SnackBar(ft.Text("Error guardando perfil."), open=True)
            page.update()

    # Volver al estilo anterior (más simple) — sin scroll interno para evitar anidamiento
    # Componentes de resumen mensual (se actualizarán tras cargar datos)
    resumen_peso_text = ft.Text("--", size=14, color=ft.colors.WHITE)
    dias_registrados_text = ft.Text("--", size=12, color=ft.colors.GREY_400)
    dias_meta_text = ft.Text("--", size=12, color=ft.colors.GREY_400)

    # Progress bars for resumen
    peso_progress = ft.ProgressBar(value=0, width=260, color=styles.ACCENT)
    dias_progress = ft.ProgressBar(value=0, width=260, color=styles.SECOND)
    meta_progress = ft.ProgressBar(value=0, width=260, color=styles.WARNING)

    def calcular_resumen_mensual():
        if not user_id:
            return
        try:
            hoy = datetime.now().date()
            hace_30 = hoy - timedelta(days=30)

            # Cargar consumo diario
            consumo = db.child("usuarios").child(user_id).child("consumo_diario").get().val() or {}
            dias_registrados = 0
            dias_meta = 0

            # Obtener requerimiento calórico de referencia
            p = perfil.get("peso", peso_field.value or "")
            a = perfil.get("altura", altura_field.value or "")
            ed = perfil.get("edad", edad_field.value or "")
            obj = perfil.get("objetivo", objetivo_val or "")
            try:
                cal_obj, *_ = calcular_requerimientos(p or 0, a or 0, ed or 21, obj or "")
            except Exception:
                cal_obj = None

            for fecha_str, nodo in (consumo.items()):
                try:
                    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                except Exception:
                    continue
                if fecha_dt < hace_30 or fecha_dt > hoy:
                    continue
                # Consideramos día registrado si tiene comidas
                if isinstance(nodo, dict) and nodo.get("comidas"):
                    dias_registrados += 1
                    # calorías del día: preferimos totales si existen, si no sumamos comidas
                    calorias_dia = None
                    try:
                        calorias_dia = float(nodo.get("calorias", 0) or 0)
                    except Exception:
                        calorias_dia = None
                    if not calorias_dia:
                        # sumar comidas
                        try:
                            s = 0.0
                            for k, v in nodo.get("comidas", {}).items():
                                if isinstance(v, dict):
                                    s += float(v.get("calorias", 0) or 0)
                            calorias_dia = s
                        except Exception:
                            calorias_dia = 0
                    if cal_obj is not None and calorias_dia <= cal_obj:
                        dias_meta += 1

            # Calcular cambio de peso en historial
            peso_hist = db.child("usuarios").child(user_id).child("peso_historial").get().val() or {}
            # filtrar por rango y ordenar
            pesos_30 = []
            for f_str, w in peso_hist.items():
                try:
                    f_dt = datetime.strptime(f_str, "%Y-%m-%d").date()
                    if hace_30 <= f_dt <= hoy:
                        pesos_30.append((f_dt, float(w)))
                except Exception:
                    continue
            pesos_30.sort(key=lambda x: x[0])
            peso_resumen = "Sin registros suficientes"
            if len(pesos_30) >= 2:
                primero = pesos_30[0][1]
                ultimo = pesos_30[-1][1]
                delta = round(ultimo - primero, 2)
                meta = perfil.get("meta_peso", "")
                if delta == 0:
                    peso_resumen = "Sin cambio en 30 días"
                else:
                    if "Perder" in meta and delta < 0:
                        peso_resumen = f"Has perdido {abs(delta)} kg"
                    elif "Ganar" in meta and delta > 0:
                        peso_resumen = f"Has ganado {abs(delta)} kg"
                    else:
                        # Mostrar signo según delta
                        if delta < 0:
                            peso_resumen = f"Cambio: -{abs(delta)} kg"
                        else:
                            peso_resumen = f"Cambio: +{abs(delta)} kg"

            # Actualizar textos y barras
            resumen_peso_text.value = peso_resumen
            dias_registrados_text.value = f"Días registrados (últimos 30 días): {dias_registrados}"
            dias_meta_text.value = f"Días que lograron la meta calórica: {dias_meta}"

            # barras: normalizamos a 30 días para los porcentajes
            try:
                dias_progress.value = min(1.0, dias_registrados / 30.0)
            except Exception:
                dias_progress.value = 0
            try:
                meta_progress.value = min(1.0, dias_meta / 30.0)
            except Exception:
                meta_progress.value = 0
            # peso: asumimos meta de 5kg como referencia para visualizar progreso
            try:
                if len(pesos_30) >= 2:
                    progress_weight = min(1.0, abs(pesos_30[-1][1] - pesos_30[0][1]) / 5.0)
                else:
                    progress_weight = 0
                peso_progress.value = progress_weight
            except Exception:
                peso_progress.value = 0

            page.update()
        except Exception as ex:
            print("Error calculando resumen mensual:", ex)

    # Llamada inicial para poblar resumen
    try:
        calcular_resumen_mensual()
    except Exception:
        pass

    # Metric small cards (Peso / Altura / BMI)
    # Calcular BMI
    try:
        peso_val = float(str(perfil.get("peso", peso_field.value or "")).replace(",", "."))
    except Exception:
        try:
            peso_val = float(str(peso_field.value or "").replace(",", "."))
        except Exception:
            peso_val = None
    try:
        altura_raw = str(perfil.get("altura", altura_field.value or ""))
        altura_f = float(altura_raw.replace(",", "."))
        if altura_f > 3:  # probable cm
            altura_m = altura_f / 100.0
        else:
            altura_m = altura_f
    except Exception:
        altura_m = None

    bmi = "--"
    if peso_val and altura_m and altura_m > 0:
        try:
            bmi_v = round(peso_val / (altura_m * altura_m), 1)
            bmi = str(bmi_v)
        except Exception:
            bmi = "--"

    metrics_row = ft.Row([
        styles.metric_card("Peso", f"{peso_val if peso_val is not None else '--'} kg", icon=None),
        ft.Container(width=12),
        styles.metric_card("Altura", f"{int(altura_m*100) if altura_m else '--'} cm", icon=None),
        ft.Container(width=12),
        styles.metric_card("IMC", bmi, icon=None)
    ], alignment=ft.MainAxisAlignment.CENTER)

    resumen_col = ft.Column([
        ft.Text("Resumen del mes", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
        ft.Divider(height=8, color="transparent"),
        ft.Column([resumen_peso_text, ft.Container(height=8), peso_progress], tight=True),
        ft.Divider(height=10, color="transparent"),
        ft.Column([dias_registrados_text, ft.Container(height=8), dias_progress], tight=True),
        ft.Divider(height=10, color="transparent"),
        ft.Column([dias_meta_text, ft.Container(height=8), meta_progress], tight=True)
    ], tight=True)

    resumen_card_ui = styles.resumen_card(resumen_col, width=340)

    # Menu actions (functional) -------------------------------------------------
    def abrir_cambiar_meta(e=None):
        # Dropdown to choose meta de peso; dialog will size to content
        options = ["Perder peso", "Ganar peso", "Mantener peso"]
        inicial = perfil.get("meta_peso", "Mantener peso")
        dd = ft.Dropdown(label="Meta de peso", value=inicial, options=[ft.dropdown.Option(o) for o in options])

        def guardar_meta(_):
            try:
                nuevo = dd.value or ""
                db.child("usuarios").child(user_id).child("perfil").update({"meta_peso": nuevo})
                perfil["meta_peso"] = nuevo
                page.snack_bar = ft.SnackBar(ft.Text("Meta de peso actualizada."), open=True)
                try:
                    calcular_resumen_mensual()
                except Exception:
                    pass
            except Exception as ex:
                print("Error actualizando meta de peso:", ex)
                page.snack_bar = ft.SnackBar(ft.Text("Error actualizando meta de peso."), open=True)
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(content=ft.Column([dd], tight=True), actions=[ft.TextButton("Cancelar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update())), ft.ElevatedButton("Guardar", on_click=guardar_meta)])
        page.dialog.open = True
        page.update()

    def abrir_actualizar_peso(e=None):
        tf = ft.TextField(label="Nuevo peso (kg)", value=str(perfil.get("peso", "")), width=200)
        def guardar_peso(_):
            try:
                nuevo = float(str(tf.value).replace(",", "."))
                fecha_hoy = datetime.now().strftime("%Y-%m-%d")
                db.child("usuarios").child(user_id).child("peso_historial").child(fecha_hoy).set(nuevo)
                db.child("usuarios").child(user_id).child("perfil").update({"peso": nuevo})
                perfil["peso"] = nuevo
                peso_field.value = str(nuevo)
                page.snack_bar = ft.SnackBar(ft.Text("Peso actualizado."), open=True)
                try:
                    calcular_resumen_mensual()
                except Exception:
                    pass
            except Exception as ex:
                print("Error actualizando peso:", ex)
                page.snack_bar = ft.SnackBar(ft.Text("Error actualizando peso."), open=True)
            page.dialog.open = False
            page.update()

        # Use tight=True so dialog height adjusts to content
        page.dialog = ft.AlertDialog(content=ft.Column([tf], tight=True), actions=[ft.TextButton("Cancelar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update())), ft.ElevatedButton("Guardar", on_click=guardar_peso)])
        page.dialog.open = True
        page.update()

    def abrir_preferencias(e=None):
        prefs = perfil.get("preferencias", {}) or {}
        veg = ft.Checkbox(label="Vegetariano", value=bool(prefs.get("vegetariano", False)))
        vegano = ft.Checkbox(label="Vegano", value=bool(prefs.get("vegano", False)))
        pesc = ft.Checkbox(label="Pescatariano", value=bool(prefs.get("pescatariano", False)))
        lact = ft.Checkbox(label="Sin lactosa", value=bool(prefs.get("sin_lactosa", False)))
        gluten = ft.Checkbox(label="Sin gluten", value=bool(prefs.get("sin_gluten", False)))
        frutos = ft.Checkbox(label="Sin frutos secos", value=bool(prefs.get("sin_frutos_secos", False)))
        bajo_sodio = ft.Checkbox(label="Bajo en sodio", value=bool(prefs.get("bajo_sodio", False)))
        bajo_azucar = ft.Checkbox(label="Bajo en azúcar", value=bool(prefs.get("bajo_azucar", False)))
        alta_prot = ft.Checkbox(label="Alta proteína", value=bool(prefs.get("alta_proteina", False)))

        def guardar_prefs(_):
            try:
                newp = {
                    "vegetariano": veg.value,
                    "vegano": vegano.value,
                    "pescatariano": pesc.value,
                    "sin_lactosa": lact.value,
                    "sin_gluten": gluten.value,
                    "sin_frutos_secos": frutos.value,
                    "bajo_sodio": bajo_sodio.value,
                    "bajo_azucar": bajo_azucar.value,
                    "alta_proteina": alta_prot.value
                }
                db.child("usuarios").child(user_id).child("perfil").update({"preferencias": newp})
                perfil["preferencias"] = newp
                page.snack_bar = ft.SnackBar(ft.Text("Preferencias guardadas."), open=True)
            except Exception as ex:
                print("Error guardando preferencias:", ex)
                page.snack_bar = ft.SnackBar(ft.Text("Error guardando preferencias."), open=True)
            page.dialog.open = False
            page.update()

        # Agrupar en dos columnas para mejor legibilidad
        col_left = ft.Column([veg, vegano, pesc, lact, gluten], tight=True)
        col_right = ft.Column([frutos, bajo_sodio, bajo_azucar, alta_prot], tight=True)
        # Wrap content in a container (no fixed height) so dialog height follows content size
        page.dialog = ft.AlertDialog(
            content=ft.Container(
                padding=10,
                content=ft.Row([col_left, ft.Container(width=24), col_right], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: (setattr(page.dialog, "open", False), page.update())),
                ft.ElevatedButton("Guardar", on_click=guardar_prefs)
            ]
        )
        page.dialog.open = True
        page.update()

    menu_card = styles.fancy_card(
        ft.Column([
            ft.Text("Perfil y Objetivos", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Divider(height=8, color="transparent"),
            ft.ListTile(title=ft.Text("Cambiar meta de peso"), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT), on_click=abrir_cambiar_meta),
            ft.ListTile(title=ft.Text("Actualizar peso"), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT), on_click=abrir_actualizar_peso),
            ft.ListTile(title=ft.Text("Preferencias alimentarias"), trailing=ft.Icon(ft.icons.CHEVRON_RIGHT), on_click=abrir_preferencias),
        ], tight=True),
        width=300,
        colors=(styles.CARD_BG, styles.BG),
        border_color=styles.SECOND
    )

    # Profile card (first card) with avatar, email and form
    profile_form = ft.Column([
        ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, size=44), radius=44, bgcolor=ft.colors.GREY_800),
        ft.Container(height=8),
        ft.Text(f"Email: {user_email}", size=14, color=ft.colors.GREY_400),
        ft.Divider(height=12, color="transparent"),
        peso_field,
        altura_field,
        edad_field,
        ft.Container(height=10),
        ft.ElevatedButton(
            text="Guardar Cambios",
            icon=ft.icons.SAVE_ROUNDED,
            style=ft.ButtonStyle(bgcolor="#6ee7b7", color="#0c0e16"),
            width=260,
            height=42,
            on_click=guardar_perfil
        ),
        ft.Container(height=6),
        ft.TextButton(
            "Cerrar Sesión",
            icon=ft.icons.LOGOUT_ROUNDED,
            on_click=lambda _: [page.user_data.clear(), page.go("/")],
            style=ft.ButtonStyle(color=ft.colors.RED_300)
        )
    ], tight=True)

    profile_card = styles.fancy_card(profile_form, width=300, colors=(styles.CARD_BG, styles.BG), border_color=styles.ACCENT)

    # Layout: stack the three cards vertically (list style) for clearer organization
    cards_col = ft.Column([
        profile_card,
        ft.Container(height=18),
        resumen_card_ui,
        ft.Container(height=18),
        menu_card
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        padding=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Text("Configuración de Perfil", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Container(height=8),
                cards_col
            ]
        )
    )
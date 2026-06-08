# Estilos reutilizables para Nutritrack (Flet)
import flet as ft

# Colores
BG = "#141720"
ACCENT = "#6ee7b7"
SECOND = "#4fc3f7"
WARNING = "#ffd54f"
CARD_BG = "#0f1114"

# Funciones para crear tarjetas
def card_container(content, width=None, height=None):
    return ft.Container(
        content=content,
        bgcolor=BG,
        padding=20,
        border_radius=12,
        border=ft.border.all(1, "rgba(255,255,255,0.04)"),
        width=width,
        height=height
    )

def fancy_card(content, width=None, height=None, colors=("#0ea5a5", "#6ee7b7"), border_color=None):
    # Gradient card with subtle border to simulate depth
    try:
        gradient = ft.LinearGradient(begin=ft.alignment.TopLeft, end=ft.alignment.BottomRight, colors=list(colors))
        inner = ft.Container(content=content, gradient=gradient, padding=16, border_radius=12, width=width, height=height)
        # outer container as subtle shadow/border
        border = ft.border.all(1, border_color or "rgba(255,255,255,0.04)")
        return ft.Container(content=inner, padding=2, border_radius=14, bgcolor="#081018", border=border)
    except Exception:
        # Fallback if gradient isn't supported in runtime
        inner = ft.Container(content=content, bgcolor=colors[-1], padding=16, border_radius=12, width=width, height=height)
        border = ft.border.all(1, border_color or "rgba(255,255,255,0.04)")
        return ft.Container(content=inner, padding=2, border_radius=14, bgcolor="#081018", border=border)

def header_text(text):
    return ft.Text(text, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)

def small_text(text):
    return ft.Text(text, size=12, color=ft.colors.GREY_400)


def metric_card(title, value, icon=None, width=110, bgcolor="#0b0d10"):
    icon_control = ft.Container()
    if icon:
        icon_control = ft.Container(content=ft.Icon(icon, color=ACCENT, size=20), padding=6)
    return ft.Container(
        width=width,
        padding=12,
        bgcolor=bgcolor,
        border_radius=12,
        content=ft.Column([
            ft.Row([icon_control, ft.Container(width=6)], alignment=ft.MainAxisAlignment.START),
            ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(title, size=12, color=ft.colors.GREY_400)
        ], tight=True)
    )


def progress_row(label, value, max_value=1.0, color=ACCENT, width=260):
    # value: 0..1 or absolute that will be normalized by max_value
    try:
        v = float(value) / float(max_value) if max_value and max_value != 0 else 0
    except Exception:
        v = 0
    v = max(0.0, min(1.0, v))
    bar = ft.ProgressBar(value=v, width=width, color=color)
    return ft.Column([
        ft.Row([ft.Text(label, size=12, color=ft.colors.WHITE60), ft.Text(f"{int(v*100)}%", size=12, color=ft.colors.GREY_400)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=6),
        bar
    ], tight=True)


def resumen_card(content, width=300):
    inner = ft.Container(content=content, padding=16, border_radius=12, bgcolor=CARD_BG)
    return ft.Container(content=inner, padding=2, border_radius=14, bgcolor="#081018", width=width)

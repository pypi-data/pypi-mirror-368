import flet as ft

from fletplus.core import FletPlusApp


class DummyPage:
    def __init__(self, platform: str = "web"):
        self.platform = platform
        self.title = ""
        self.controls = []
        self.theme = None
        self.theme_mode = None
        self.scroll = None
        self.horizontal_alignment = None
        self.updated = False

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.updated = True

def test_fletplus_app_initialization_and_routing():
    # Definir dos pantallas de prueba
    def home_view():
        return ft.Text("Inicio")

    def users_view():
        return ft.Text("Usuarios")

    routes = {
        "Inicio": home_view,
        "Usuarios": users_view
    }

    sidebar_items = [
        {"title": "Inicio", "icon": ft.icons.HOME},
        {"title": "Usuarios", "icon": ft.icons.PEOPLE}
    ]

    # Crear instancia falsa de la página
    page = DummyPage()

    # Crear la app sin iniciar Flet
    app = FletPlusApp(page, routes, sidebar_items, title="TestApp")

    # Simular construcción
    app.build()

    # Verificaciones básicas
    assert page.title == "TestApp"
    assert len(page.controls) == 1  # Un solo ft.Row
    assert app.content_container.content is not None
    assert isinstance(app.content_container.content, ft.Text)
    assert app.content_container.content.value == "Inicio"

    # Simular navegación a la segunda página
    app._on_nav(1)
    assert app.content_container.content.value == "Usuarios"


def test_fletplus_app_without_routes():
    page = DummyPage()
    app = FletPlusApp(page, {})
    app.build()
    assert app.content_container.content is None


def test_fletplus_app_invalid_route_index():
    def home_view():
        return ft.Text("Inicio")

    routes = {"Inicio": home_view}

    page = DummyPage()
    app = FletPlusApp(page, routes)
    app.build()

    # Guardar contenido actual
    original_content = app.content_container.content

    # Índice fuera de rango positivo
    app._on_nav(5)
    assert app.content_container.content == original_content

    # Índice negativo
    app._on_nav(-1)
    assert app.content_container.content == original_content

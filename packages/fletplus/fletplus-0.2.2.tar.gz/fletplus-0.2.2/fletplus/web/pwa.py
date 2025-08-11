"""Herramientas para habilitar PWA en proyectos FletPlus.

Este módulo permite generar el ``service_worker.js`` encargado de
cachear recursos estáticos y el ``manifest.json`` que describe la PWA.
Incluye además una función para registrar ambos elementos en una página
Flet.
"""

from __future__ import annotations

from pathlib import Path
import json
from urllib.parse import urlparse
from html import escape
from typing import Iterable, List, Dict

import flet as ft


def generate_service_worker(static_files: Iterable[str], output_dir: Path) -> Path:
    """Genera ``service_worker.js`` en ``output_dir``.

    :param static_files: Rutas relativas de los recursos a cachear.
    :param output_dir: Directorio donde guardar el archivo.
    :return: Ruta al ``service_worker.js`` creado.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sw_path = output_dir / "service_worker.js"

    files = list(static_files)
    content = (
        "const CACHE_NAME = 'fletplus-cache-v1';\n" +
        f"const STATIC_ASSETS = {json.dumps(files)};\n\n" +
        "self.addEventListener('install', event => {\n" +
        "  event.waitUntil(\n" +
        "    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))\n" +
        "  );\n" +
        "});\n\n" +
        "self.addEventListener('fetch', event => {\n" +
        "  event.respondWith(\n" +
        "    caches.match(event.request).then(resp => resp || fetch(event.request))\n" +
        "  );\n" +
        "});\n"
    )
    sw_path.write_text(content, encoding="utf-8")
    return sw_path


def generate_manifest(name: str, icons: List[Dict], start_url: str, output_dir: Path) -> Path:
    """Genera ``manifest.json`` con los parámetros indicados.

    :param name: Nombre de la aplicación.
    :param icons: Lista de diccionarios con la información de iconos.
    :param start_url: URL inicial de la PWA.
    :param output_dir: Directorio donde guardar el archivo.
    :return: Ruta al ``manifest.json`` creado.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest = {
        "name": name,
        "start_url": start_url,
        "display": "standalone",
        "icons": icons,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def register_pwa(
    page: ft.Page,
    manifest_url: str = "manifest.json",
    service_worker_url: str = "service_worker.js",
) -> None:
    """Registra ``manifest.json`` y ``service_worker.js`` en una página Flet.

    Añade la etiqueta ``link`` del manifest y registra el Service Worker a
    través de un pequeño script. Los parámetros ``manifest_url`` y
    ``service_worker_url`` deben ser rutas relativas del mismo origen.
    """
    def _validate_url(url: str, name: str) -> None:
        parsed = urlparse(url)
        if parsed.netloc:
            raise ValueError(f"{name.capitalize()} URL must be same origin")
        if parsed.scheme not in ("", "http", "https"):
            raise ValueError(f"Invalid {name} URL")
        if any(c in url for c in ' <>"\''):
            raise ValueError(f"Invalid {name} URL")

    _validate_url(manifest_url, "manifest")
    _validate_url(service_worker_url, "service worker")

    page.add_head_html(
        f'<link rel="manifest" href="{escape(manifest_url, quote=True)}">'
    )
    page.add_script(
        "if ('serviceWorker' in navigator) {"
        + f"navigator.serviceWorker.register({json.dumps(service_worker_url)});"
        + "}"
    )

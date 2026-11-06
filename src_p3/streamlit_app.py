"""Plantilla: aplicación Streamlit conectada a tu servicio de IA.

Completa SOLO las partes marcadas con TODO (del 0 al 6; el 5 tiene subapartados
a y b). El resto ya está hecho.
Este es el único fichero de código que tienes que completar (además del README).
Autores: David Tella, Aaron Hernandez

Qué hace la app: el usuario introduce 2 variables (ingreso medio y número de
habitaciones); la app completa el resto con valores por defecto, comprueba que
están las 8 variables, llama a la API (POST /predict), transforma la respuesta
a dólares y la muestra.

Dónde está cada apartado:
    a) Conexión ............. TODO 0: URL de la API; TODO 1: la petición POST
    b) Datos de entrada ..... TODO 2: find_missing()
    c) Datos de salida ...... TODO 3: format_price(); TODO 4: mostrar el precio
    d) Interfaz ............. TODO 6: campo de número de habitaciones
    e) Control de errores ... TODO 5a: fallo de comunicación; TODO 5b: respuesta de error
       (la documentación de la API va en el README)
"""
import logging
import time

import requests
import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("app")

# Nombres que aparecerán en la interfaz (necesario para las capturas).
AUTORES = "David Tella, Aaron Hernandez"

# TODO 0 (apartado a): URL pública de tu API en Render (sin barra final).
API_URL = "https://practica3-ia-davidt-aaronh.onrender.com"
TIMEOUT = 90

# Las 8 variables que necesita el modelo.
FEATURE_NAMES = [
    "MedInc", "HouseAge", "AveRooms", "AveBedrms",
    "Population", "AveOccup", "Latitude", "Longitude",
]

# Variables que NO se piden al usuario (valores aproximados de la mediana del
# dataset de California Housing).
DEFAULTS = {
    "HouseAge": 29.0,
    "AveBedrms": 1.05,
    "Population": 1166.0,
    "AveOccup": 2.8,
    "Latitude": 34.26,
    "Longitude": -118.49,
}


def find_missing(payload: dict) -> list[str]:
    """Devuelve las variables de FEATURE_NAMES que faltan en `payload`."""
    return [nombre for nombre in FEATURE_NAMES if payload.get(nombre) is None]


# TODO 3 (apartado c)
def format_price(med_house_val: float) -> str:
    """Convierte la salida del modelo a un texto legible en dólares."""
    precio = med_house_val * 100_000
    return f"${precio:,.0f}"


# ---------------------------------------------------------------- Interfaz --
st.set_page_config(page_title="Precio de casas en California")
st.title("Precio de casas en California")
st.caption(f"{AUTORES} - P3")
st.write("Introduce los datos de la zona y estima el precio medio de sus viviendas.")

# Barra lateral: permite cambiar de servidor y provocar errores de prueba.
api_url = st.sidebar.text_input("URL de la API", API_URL).rstrip("/")
simulate_missing = st.sidebar.checkbox("Prueba: omitir HouseAge de la petición")
skip_validation = st.sidebar.checkbox(
    "Prueba: saltar la validación local (provoca un 422 de la API)"
)

# Variables clave que introduce el usuario.
med_inc = st.number_input(
    "Ingreso medio de la zona (decenas de miles de $)",
    min_value=0.0, max_value=15.0, value=3.5, step=0.1,
)

# TODO 6 (apartado d): campo de entrada para el número de habitaciones
ave_rooms = st.number_input(
    "Número medio de habitaciones por vivienda",
    min_value=1.0, max_value=15.0, value=5.2, step=0.1,
)


if st.button("Estimar precio"):
    payload = {
        **DEFAULTS,
        "MedInc": med_inc,
        "AveRooms": ave_rooms,
    }
    if simulate_missing:  # solo para la prueba de errores
        payload.pop("HouseAge", None)

    # Apartado b: validar los datos ANTES de enviarlos.
    missing = find_missing(payload)
    if skip_validation and missing:
        logger.warning("Validación local saltada (prueba). Faltan: %s", missing)
    elif missing:
        logger.warning("Petición no enviada, faltan: %s", missing)
        st.error(f"Faltan variables obligatorias: {', '.join(missing)}")
        st.stop()

    if "<" in api_url:  # sigue el valor de ejemplo de Render: falta el TODO 0
        st.error("Configura la URL de la API (TODO 0 o barra lateral).")
        st.stop()

    try:
        start = time.perf_counter()
        with st.spinner("Consultando la API (la primera vez puede tardar más de un minuto)..."):
            # TODO 1 (apartado a): petición POST al endpoint /predict
            response = requests.post(api_url + "/predict", json=payload, timeout=TIMEOUT)
        elapsed_ms = (time.perf_counter() - start) * 1000
    # TODO 5a (apartado e): mensajes claros para cada fallo de comunicación
    except requests.Timeout as exc:
        logger.error("Timeout con %s: %s", api_url, exc)
        st.error(
            f"La API no respondió en {TIMEOUT} segundos. Si el servicio de Render "
            "estaba dormido, espera un minuto y vuelve a intentarlo."
        )
    except requests.ConnectionError as exc:
        logger.error("Fallo de conexión con %s: %s", api_url, exc)
        st.error(
            "No se pudo conectar con la API. Comprueba que la URL de la barra "
            "lateral es correcta y que el servicio está activo en Render."
        )
    except requests.RequestException as exc:
        logger.error("Error en la petición a %s: %s", api_url, exc)
        st.error("La petición a la API no es válida. Revisa la URL (debe empezar por https://).")
    else:
        logger.info("POST %s/predict -> HTTP %s en %.0f ms", api_url, response.status_code, elapsed_ms)
        if response.status_code == 200:
            try:
                med_house_val = float(response.json()["MedHouseVal"])
            except (ValueError, KeyError, TypeError):
                logger.error("Respuesta inesperada: %s", response.text[:200])
                st.error("La API respondió, pero con un formato inesperado. ¿Es correcta la URL?")
                st.stop()
            # TODO 4 (apartados c y d): muestra el precio formateado y el valor crudo
            st.metric("Precio estimado", format_price(med_house_val))
            st.caption(f"Valor devuelto por la API (sin formatear): {med_house_val}")
        # TODO 5b (apartado e): respuestas de error de la API con mensajes claros
        elif response.status_code == 422:
            try:
                campos = [str(e["loc"][-1]) for e in response.json().get("detail", [])]
            except (ValueError, KeyError, TypeError, IndexError):
                campos = []
            detalle = f" Campos con problemas: {', '.join(campos)}." if campos else ""
            st.error(f"La API ha rechazado los datos enviados (error 422).{detalle}")
        elif response.status_code == 404:
            st.error(
                "La dirección de la API no existe (error 404). Revisa que la URL "
                "de la barra lateral apunta a tu servicio FastAPI."
            )
        elif response.status_code == 503:
            st.error("El modelo todavía no está cargado en el servidor (error 503). Prueba en unos segundos.")
        elif response.status_code >= 500:
            st.error(f"Error interno del servidor de IA (error {response.status_code}). Inténtalo más tarde.")
        else:
            st.error(f"Respuesta inesperada de la API (código {response.status_code}).")

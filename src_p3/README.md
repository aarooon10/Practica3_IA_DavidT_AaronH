# Aplicación Streamlit - Precio de casas en California

Aplicación web (Streamlit) conectada a un servicio de IA en FastAPI desplegado en Render para predecir precios de viviendas.

**Autores:** David Tella, Aaron Hernandez (P3)

## Servicios y Ejecución
- **API FastAPI:** `https://practica3-ia-davidt-aaronh.onrender.com/`
- **Local:** 
  - API: `uvicorn app:app --reload`
  - Interfaz: `streamlit run streamlit_app.py`

## Despliegue en Render
- **API:** Build Command: `pip install -r requirements.txt` | Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Interfaz:** Build Command: `pip install -r requirements.txt` | Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Documentación de la API (`POST /predict`)
- **Entrada (JSON):** 8 variables obligatorias (`MedInc`, `HouseAge`, `AveRooms`, `AveBedrms`, `Population`, `AveOccup`, `Latitude`, `Longitude`).
- **Respuesta Exitosa (200 OK):**
  ```json
  {
    "MedHouseVal": 1.5126018234536092
  }
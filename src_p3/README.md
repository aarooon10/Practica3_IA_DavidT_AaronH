# Práctica 3 - Precio de casas en California (FastAPI + Streamlit)

Aplicación web en Streamlit conectada a un servicio de IA en FastAPI. Los dos servicios están desplegados en Render.

**Autores:** David Tella Miranda, Aaron Hernández Ocejo (P3)

## URLs públicas
- **API (FastAPI):** https://practica3-ia-davidt-aaronh.onrender.com
- **Interfaz (Streamlit):** https://practica3-streamlit-davidt-aaronh.onrender.com

## Ejecución en local
```bash
cd src_p3
pip install -r requirements.txt
uvicorn app:app --reload            # API en http://127.0.0.1:8000
streamlit run streamlit_app.py      # Interfaz en http://localhost:8501
```

## Despliegue en Render
Root Directory en Render: `src_p3`

| Servicio | Build Command | Start Command |
|---|---|---|
| API | `pip install -r requirements.txt` | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| Interfaz | `pip install -r requirements.txt` | `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |

## Documentación de la API

### `GET /` - Health-check
Respuesta (200 OK):
```json
{"status": "ok", "autores": "David Tella, Aaron Hernández P3"}
```

### `POST /predict` - Predicción
Recibe un JSON con las 8 variables obligatorias (todas numéricas):

| Variable | Significado |
|---|---|
| `MedInc` | Ingreso medio de la zona (decenas de miles de $) |
| `HouseAge` | Edad media de las viviendas (años) |
| `AveRooms` | Número medio de habitaciones por vivienda |
| `AveBedrms` | Número medio de dormitorios por vivienda |
| `Population` | Población de la zona |
| `AveOccup` | Ocupantes medios por vivienda |
| `Latitude` | Latitud |
| `Longitude` | Longitud |

**Ejemplo de petición:**
```bash
curl -X POST https://practica3-ia-davidt-aaronh.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"MedInc": 3.5, "HouseAge": 29.0, "AveRooms": 5.2, "AveBedrms": 1.05, "Population": 1166.0, "AveOccup": 2.8, "Latitude": 34.26, "Longitude": -118.49}'
```

**Ejemplo de respuesta (200 OK):**
```json
{"MedHouseVal": 1.5126018234536092}
```
El valor está en cientos de miles de dólares: 1.5126 → **$151,260**.

### Errores
| Código | Cuándo ocurre | Mensaje que ve el usuario en Streamlit |
|---|---|---|
| 422 | Falta una variable o no es numérica | "La API ha rechazado los datos enviados (error 422). Campos con problemas: HouseAge." |
| 404 | La URL no apunta a la API | "La dirección de la API no existe (error 404)…" |
| 503 | El modelo no está cargado | "El modelo todavía no está cargado en el servidor…" |
| Sin respuesta | URL incorrecta o servicio caído | "No se pudo conectar con la API…" |

Ejemplo de respuesta 422 de la API:
```json
{"detail": [{"type": "missing", "loc": ["body", "HouseAge"], "msg": "Field required"}]}
```

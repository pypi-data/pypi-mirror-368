# Track Flow / Flujo de Seguimiento

**ES / Español 🇪🇸**

`track-flow` es una librería modular en Python diseñada para implementar un pipeline ETL completo, ideal para flujos de trabajo donde se requiere extracción, transformación y carga de datos de forma eficiente y reutilizable.

---

## 🚀 Características

- Extracción desde APIs externas (por ejemplo, Spotify)
- Transformación de datos en DTOs
- Almacenamiento en formato Parquet
- Carga en Amazon S3 u otros destinos
- Configuración flexible mediante variables de entorno
- Uso como librería o desde línea de comandos

---

## ⚙️ Variables de entorno necesarias

Debes definir un archivo `.env` en la raíz de tu proyecto con las siguientes variables:

```env
# Claves AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=

# Bucket de destino
AWS_BUCKET_SONG_NAME=

# Datos a procesar
TRACK_LIST=2U3UUpx6ocHXgvcXmq0YBw  # ID de playlist o track de Spotify

#CLIENT AND CLIENT SECRET SPOTIFY 

CLIENT_ID_SPOTIFY= 
CLIENT_SECRET_SPOTIFY=

# Directorio de salida local
ETL_OUTPUT_DIR=output
```

---

## 📦 Instalación

```bash
pip install track-flow
```

---

## 💻 Uso básico

Como script:

```bash
trackflow
```

Como módulo de Python:

```python
from track_flow.main import main

main()
```

---

## 🧠 Requisitos

- Python >= 3.9
- Tener configurado el archivo `.env`
- Acceso válido a la API de Spotify y AWS

---

## 🪪 Licencia

MIT © Facu Vega  
https://github.com/facuvegaingenieer

---

**EN / English 🇬🇧**

`track-flow` is a modular Python library that implements a full ETL pipeline, ideal for workflows requiring robust data extraction, transformation, and loading in a reusable and configurable way.

---

## 🚀 Features

- Extraction from external APIs (e.g., Spotify)
- Data transformation into DTOs
- Storage as Parquet files
- Upload to Amazon S3 or other destinations
- Environment-based configuration
- Usable as a library or from the command line

---

## ⚙️ Required Environment Variables

You must define a `.env` file at the root of your project with the following variables:

```env
# AWS credentials
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=

# S3 Bucket
AWS_BUCKET_SONG_NAME=

# Data to extract
TRACK_LIST=2U3UUpx6ocHXgvcXmq0YBw  # Playlist or track ID from Spotify

# Local output directory
ETL_OUTPUT_DIR=output
```

---

## 📦 Installation

```bash
pip install track-flow
```

---

## 💻 Basic Usage

As CLI:

```bash
trackflow
```

As a Python module:

```python
from track_flow.main import main

main()
```

---

## 🧠 Requirements

- Python >= 3.9
- Valid `.env` file
- Access to Spotify and AWS

---

## 🪪 License

MIT © Facu Vega  
https://github.com/facuvegaingenieer
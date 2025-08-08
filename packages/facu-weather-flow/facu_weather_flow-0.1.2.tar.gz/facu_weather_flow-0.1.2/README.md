# Facu Weather Flow

**Facu Weather Flow** es una librería de Python modular que implementa un pipeline ETL para procesar datos del clima de cualquier ciudad que necesites.

**Facu Weather Flow** is a modular Python library that implements an ETL pipeline to process weather data for any city you need.

---

## 🚀 Características / Features

- Extracción de datos desde la API de OpenWeatherMap  
  Data extraction from the OpenWeatherMap API
- Transformación a DTOs estructurados  
  Transformation into structured DTOs
- Almacenamiento como archivos Parquet  
  Storage as Parquet files
- Carga directa en un bucket S3 en AWS  
  Direct upload to an AWS S3 bucket
- Configuración flexible mediante variables de entorno  
  Flexible configuration through environment variables
- Uso como librería o desde la línea de comandos (`weather-flow`)  
  Usable as a library or from the command line (`weather-flow`)

---

## 📦 Instalación / Installation

```bash
pip install facu-weather-flow
```

---

## 🧪 Uso desde CLI / CLI Usage

```bash
weather-flow
```

O como módulo / Or as a module:

```bash
python -m facu_weather_flow
```

---

## ⚙️ Variables de entorno / Environment Variables

La librería requiere las siguientes variables, definidas en un archivo `.env` o como variables del entorno:  
The library requires the following variables, defined in a `.env` file or as environment variables:

```env
OPENWEATHERMAP_API_KEY=tu_api_key_openweathermap / your_openweathermap_api_key
CITY_DATA=nombre_ciudad_o_archivo / city_name_or_file
AWS_ACCESS_KEY_ID=tu_access_key / your_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key / your_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_WEATHER_BUCKET_NAME=nombre_del_bucket_s3 / your_s3_bucket_name
WEATHER_OUTPUT_DIR=/ruta/de/salida/local / local_output_path
```

---

## 📚 Ejemplo de uso como módulo / Example module usage

```python
from facu_weather_flow.main import run_pipeline

run_pipeline()
```

---

## 🧊 Licencia / License

MIT © Facu Vega
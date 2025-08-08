from extract.extract import ExtractorWeather
from transform.transform import trasformData
from load.load import loaderS3
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


def run_weather_pipeline() -> None:
    logging.info("Iniciando pipeline ETL de clima...")

    # 1. Extraer
    logging.info("Extrayendo datos...")
    data = ExtractorWeather.extract()

    # 2. Transformar
    logging.info("Transformando datos...")
    data_address = trasformData.trasform_data(data)

    # 3. Cargar
    logging.info(f"Cargando datos desde: {data_address}")
    loaderS3.loadData(data_address)

    logging.info("Pipeline finalizado correctamente.")


# Solo se ejecuta si corrés el archivo directamente
if __name__ == "__main__":
    run_weather_pipeline()


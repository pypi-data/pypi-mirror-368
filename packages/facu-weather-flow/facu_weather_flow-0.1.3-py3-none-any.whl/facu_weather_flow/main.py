from extract.extract import ExtractorWeather
from transform.transform import trasformData
from load.load import loaderS3
from dotenv import load_dotenv

load_dotenv()


class ETL:
    def run(self):
        # 1. Extraer
        data = ExtractorWeather.extract()

        # 2. Transformar
        data_address = trasformData.trasform_data(data)

        # 3. Cargar
        loaderS3.loadData(data_address)


def main():
    pipeline = ETL()
    pipeline.run()


if __name__ == "__main__":
    main()


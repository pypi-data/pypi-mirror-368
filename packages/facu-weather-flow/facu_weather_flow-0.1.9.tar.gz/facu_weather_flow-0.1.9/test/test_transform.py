from facu_weather_flow.transform.transform import trasformData
import pyarrow.parquet as pq

data_mock = {
    "name": "Santa fe",
    "sys": {"country": "AR"},
    "main": {"temp": 12.3, "feels_like": 10.5, "humidity": 78},
    "wind": {"speed": 5.2},
    "dt": 1723315000
}


salida = trasformData.trasform_data(data_mock)
print("Parquet generado en:", salida)

table = pq.read_table(salida)
print(table.schema)

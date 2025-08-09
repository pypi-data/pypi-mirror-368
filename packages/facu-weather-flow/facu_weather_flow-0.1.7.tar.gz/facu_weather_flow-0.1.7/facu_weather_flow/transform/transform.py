from ..contracts.transformer import trasform
from ..DTO.jsonToDto import TrackDTO
from ..utils.filemanager import get_output_path
import pandas as pd


class trasformData(trasform):
    @classmethod
    def trasform_data(cls, data: dict) -> str:
        try:
            dataclean = TrackDTO(
                ciudad=data["name"],
                pais=data["sys"]["country"],
                temperatura=data["main"]["temp"],
                velocidad_viento=data["wind"]["speed"],
                sensacion_termica=data["main"]["feels_like"],
                humedad=data["main"]["humidity"],
                timestamp=data["dt"],
            )

            dto_dic = dataclean.__dict__
            df = pd.DataFrame([dto_dic])

            output_path = get_output_path("weather_dtos.parquet")
            df.to_parquet(output_path, index=False)
            return output_path

        except Exception as e:
            print(e)

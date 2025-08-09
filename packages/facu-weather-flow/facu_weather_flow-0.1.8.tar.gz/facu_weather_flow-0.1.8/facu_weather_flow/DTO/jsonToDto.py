from dataclasses import dataclass


@dataclass
class TrackDTO:
    ciudad: str
    pais: str
    temperatura: float
    velocidad_viento: float
    sensacion_termica: float
    humedad: int
    timestamp: int

    @property
    def hace_frio(self) -> bool:
        return self.temperatura < 15

    @property
    def viento_fuerte(self) -> bool:
        return self.velocidad_viento > 8.33  # ≈ 30 km/h

    @property
    def descripcion(self) -> str:
        estado = []
        estado.append("frío" if self.hace_frio else "templado/cálido")
        estado.append("viento fuerte" if self.viento_fuerte else "viento normal")
        return f"Clima: {' y '.join(estado)}"

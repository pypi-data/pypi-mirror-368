from ..contracts.trasformer import transformer
from ..DTO.dto import TrackDTO, dataframe_to_track_dtos
from ..utils.file_manager import get_output_path
import pandas as pd
from typing import List
import os


class transform_to_DTO(transformer):
    @classmethod
    def transform(cls, df: pd.DataFrame) -> str:
        try:
            track_dtos = dataframe_to_track_dtos(df)

            df_resultado = pd.DataFrame([dto.__dict__ for dto in track_dtos])

            output_path = get_output_path("track_dtos.parquet")

            df_resultado.to_parquet(output_path, index=False)
            return output_path
        except Exception as e:
            print(f"error al querer obtener token de api {e}")
            return None

    def __call__(self, df: pd.DataFrame) -> str:
        return self.transform(df)

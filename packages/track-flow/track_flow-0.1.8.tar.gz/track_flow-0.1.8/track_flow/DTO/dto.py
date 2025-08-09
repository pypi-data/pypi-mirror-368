from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class TrackDTO:
    name: str
    artist: str
    album: str
    id: str
    duration_ms: int


def dataframe_to_track_dtos(df: pd.DataFrame) -> List[TrackDTO]:
    REQUIRED_COLUMNS = {"name", "artist", "album", "id", "duration_ms"}
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError(
            f"El DataFrame no tiene las columnas requeridas: {REQUIRED_COLUMNS}"
        )

    return [
        TrackDTO(
            name=row["name"],
            artist=row["artist"],
            album=row["album"],
            id=row["id"],
            duration_ms=int(row["duration_ms"]),
        )
        for _, row in df.iterrows()
    ]

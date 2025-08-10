from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
from datetime import datetime


@dataclass
class TrackDTO:
    name: str
    artist: str
    album: str
    id: str
    duration_ms: int
    date: str

def dataframe_to_track_dtos(df: pd.DataFrame, date_str: Optional[str] = None) -> List[TrackDTO]:
    REQUIRED_COLUMNS = {"name", "artist", "album", "id", "duration_ms"}
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError(
            f"El DataFrame no tiene las columnas requeridas: {REQUIRED_COLUMNS}"
        )
    if date_str is None:
        date_str = datetime.now().strftime("%d/%m/%y")
    return [
        TrackDTO(
            name=row["name"],
            artist=row["artist"],
            album=row["album"],
            id=row["id"],
            duration_ms=int(row["duration_ms"]),
            date=date_str,
        )
        for _, row in df.iterrows()
    ]

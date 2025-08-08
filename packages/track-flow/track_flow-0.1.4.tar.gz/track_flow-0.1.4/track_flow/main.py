from extract.extract import extraccion_Api
from transform.transform import transform_to_DTO
from load.load import LoaderS3
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_tracks_etl() -> None:
    logging.info("Iniciando ETL de tracks de Spotify...")

    df = extraccion_Api.extract()
    output_path = transform_to_DTO.transform(df)
    LoaderS3.load(output_path, "parquets/track_dtos.parquet")

    logging.info("ETL completado exitosamente.")


if __name__ == "__main__":
    run_tracks_etl()
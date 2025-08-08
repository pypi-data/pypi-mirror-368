from extract.extract import extraccion_Api
from transform.transform import transform_to_DTO
from load.load import LoaderS3
from dotenv import load_dotenv

load_dotenv()

class tracks_spotify:
    def run(self):
        df = extraccion_Api.extract()
        output_path = transform_to_DTO.transform(df)
        LoaderS3.load(output_path, "parquets/track_dtos.parquet")


if __name__ == "__main__":
    etl = tracks_spotify()
    etl.run()
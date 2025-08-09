from contracts.extractor import extractor
import requests
import os
import base64
import pandas as pd
import json




class extraccion_Api(extractor):
    @classmethod
    def get_token(cls):
        try:
            client_id = os.getenv("CLIENT_ID_SPOTIFY")
            cliente_Secret = os.getenv("CLIENT_SECRET_SPOTIFY")
            auth_str = f"{client_id}:{cliente_Secret}"
            b64_auth_str = base64.b64encode(auth_str.encode()).decode()
            headers = {
                "Authorization": f"Basic {b64_auth_str}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {"grant_type": "client_credentials"}

            response = requests.post(
                "https://accounts.spotify.com/api/token", headers=headers, data=data
            )
            response.raise_for_status()

            return response.json()["access_token"]
        except Exception as e:
            print(f"error al querer obtener token de api {e}")
        return None

    @classmethod
    def extract(csl):
        try:
            token = csl.get_token()
            headers = {"Authorization": f"Bearer {token}"}

            playlist_id = os.getenv("TRACK_LIST")
            if not playlist_id:
                print("Error: La variable de entorno 'TRACK_LIST' no está configurada.")
                return None

            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100&offset=0"

            response = requests.get(url, headers=headers)
            data = response.json()

            items = data.get("items", [])

            tracks = []
            for item in items:
                track = item.get("track")
                if track:
                    tracks.append(
                        {
                            "name": track.get("name"),
                            "artist": ", ".join(
                                [a["name"] for a in track.get("artists", [])]
                            ),
                            "album": track.get("album", {}).get("name"),
                            "id": track.get("id"),
                            "duration_ms": track.get("duration_ms"),
                        }
                    )

            df_tracks = pd.DataFrame(tracks)

            return df_tracks

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión o respuesta HTTP: {e}")
        except ValueError:
            print("Error: La respuesta de la API no es un JSON válido.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al obtener la playlist: {e}")
        return None

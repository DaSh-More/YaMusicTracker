import httpx
import json5


def get_current_track(client) -> dict:
    r = httpx.get(
        f"https://api.mipoh.ru/get_current_track_beta?ya_token={client.token}"
    )
    return json5.loads(r.text or "{}")

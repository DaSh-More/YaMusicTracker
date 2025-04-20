import asyncio

from bestconfig import Config
from database import DB
from loguru import logger
from utils import get_current_track
from yandex_music import ClientAsync


def create_dsn(config: Config):
    return "postgresql+psycopg://{}:{}@{}:{}/{}".format(
        config.get("PG_USER"),
        config.get("PG_PASSWORD"),
        config.get("PG_URL"),
        config.get("PG_PORT"),
        config.get("PG_DB"),
    )


async def check_track(
    client: ClientAsync,
    db: DB,
    delay: int,
    max_delay: int,
    min_listen_time: int,
) -> int:
    current_track = get_current_track(client)
    if current_track["track"]["track_id"] == db.get_last_track():
        logger.info(f'track "{current_track["track"]["title"]}" already in db')
    elif int(current_track["progress_ms"]) >= min_listen_time * 1000:
        db.add_track(current_track)
        logger.info(f'track "{current_track["track"]["title"]}" added to db')
    if current_track["paused"]:
        return delay

    time_to_end = (
        int(current_track["duration_ms"]) - int(current_track["progress_ms"])
    ) / 1000

    time_to_min_listen_time = min_listen_time - int(
        current_track["progress_ms"] / 1000
    ) 

    if time_to_min_listen_time > 0:
        return time_to_min_listen_time
    return min(max_delay, time_to_end)


async def mainloop(client: ClientAsync, db: DB, config: Config):
    await client.init()
    min_listen_time = config.get("min_listen_time_s")
    delay = config.get("delay_s")
    max_delay = config.get("max_delay_s")
    acs = await client.accountStatus()
    db.set_user_id(acs.account.login)

    while True:
        time_sleep = await check_track(client, db, delay, max_delay, min_listen_time)
        logger.info(f"sleep {time_sleep} s")
        await asyncio.sleep(time_sleep)


if __name__ == "__main__":
    config = Config()
    client = ClientAsync(config.get("YM_TOKEN"))
    base = DB(create_dsn(config))
    asyncio.run(mainloop(client, base, config))

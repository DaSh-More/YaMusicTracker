from datetime import datetime as dt
from datetime import timedelta

from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase): ...


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    track_title: Mapped[str] = mapped_column(String, nullable=False)
    added_at: Mapped[dt] = mapped_column(DateTime)


class DB:
    def __init__(self, dsn, user_id=None):
        self.user_id = user_id
        self.engine = create_engine(dsn)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # Создаем базу данных и таблицы
        self.__last_track = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def add_track(self, track: dict):
        track_id = int(track["track"]["track_id"])
        self.__last_track = track_id
        track_title = track["track"]["title"]
        if self.get_last_track() == track_id:
            return
        added_at = dt.now() - timedelta(milliseconds=int(track["progress_ms"]))
        with self.Session() as session:
            new_track = Track(
                user_id=self.user_id,
                track_id=track_id,
                track_title=track_title,
                added_at=added_at,
            )
            session.add(new_track)
            session.commit()

    def get_last_track(self) -> int:
        if self.__last_track is None:
            with self.Session() as session:
                self.__last_track = (
                    session.query(Track)
                    .filter(Track.user_id == self.user_id)
                    .order_by(Track.added_at.desc())
                    .first()
                )
            self.__last_track = (
                0 if self.__last_track is None else self.__last_track.track_id
            )

        return self.__last_track

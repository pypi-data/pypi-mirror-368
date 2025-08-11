from abc import ABC, abstractmethod

from typing import List
from anime_api_scraper.models.data_models import (
    SearchResponse,
    AnimeInfo,
    LatestAnime,
    LatestEpisodes,
    Links,
)


class BaseScraper(ABC):
    """
    Clase base para los scrapers de anime.
    No instanciar directamente, usar las clases derivadas.
    Esta clase define la estructura básica y los métodos comunes
    """

    def __init__(self, *args, **kwargs):
        if self.__class__ is BaseScraper:
            raise TypeError(
                "BaseScraper is an abstract class and cannot be instantiated directly."
            )

    @abstractmethod
    def search(self, name_anime: str = "", pagina: int = 0) -> SearchResponse:
        pass

    @abstractmethod
    def get_anime_info(self, anime_id: str) -> AnimeInfo:
        pass

    @abstractmethod
    def get_latest_animes(self) -> List[LatestAnime]:
        pass

    @abstractmethod
    def get_latest_episodes(self) -> List[LatestEpisodes]:
        pass

    @abstractmethod
    def get_links(self, anime_id: str, episode: str) -> List[Links]:
        pass

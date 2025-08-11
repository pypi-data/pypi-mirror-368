from abc import ABC, abstractmethod
from typing import List
from requests import Response

from anime_api_scraper.models.data_models import (
    AnimeInfo,
    LatestAnime,
    SearchResponse,
    LatestEpisodes,
    Links,
)


class BaseProcessors(ABC):
    """
    Clase base para los procesadores de datos.
    No instanciar directamente, usar las clases derivadas.
    """

    def __init__(self, *args, **kwargs):
        if self.__class__ is BaseProcessors:
            raise TypeError(
                "BaseProcessors is an abstract class and cannot be instantiated directly."
            )

    @abstractmethod
    def process_search(self, response: Response) -> SearchResponse:
        pass

    @abstractmethod
    def process_anime_info(self, response: Response, anime_id: str) -> AnimeInfo:
        pass

    @abstractmethod
    def process_latest_animes(self, response: Response) -> List[LatestAnime]:
        pass

    @abstractmethod
    def process_latest_episodes(self, response: Response) -> List[LatestEpisodes]:
        pass

    @abstractmethod
    def process_links(self, response: Response) -> List[Links]:
        pass

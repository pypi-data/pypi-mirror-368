from .base_services import BaseServices
from anime_api_scraper.scraper.animeflv_scraper import AnimeFLVScraper
from anime_api_scraper.models.data_models import (
    SearchResponse,
    AnimeInfo,
    LatestAnime,
    LatestEpisodes,
    Links,
)
from typing import List, Optional
import logging


class AnimeFLVServices(BaseServices):
    """
    Servicio principal para interactuar con AnimeFLV.

    Este servicio actúa como una capa de abstracción entre el cliente
    y el scraper, proporcionando una API limpia y manejo de recursos optimizado.
    """

    def __init__(self):
        """
        Inicializa el servicio de AnimeFLV.

        El scraper se crea de forma lazy (solo cuando se necesite)
        para optimizar el uso de recursos.
        """
        super().__init__()
        self._scraper: Optional[AnimeFLVScraper] = None
        self._logger = logging.getLogger(__name__)

    @property
    def scraper(self) -> AnimeFLVScraper:
        """
        Obtiene el scraper, creándolo si no existe (lazy loading).

        Returns:
            AnimeFLVScraper: Instancia del scraper configurada y lista para usar
        """
        if self._scraper is None:
            self._scraper = AnimeFLVScraper()
            self._logger.debug("Scraper inicializado")
        return self._scraper

    def search_anime(self, name_anime: str = "", pagina: int = 0) -> SearchResponse:
        """
        Realiza una búsqueda de animes en AnimeFLV.

        Args:
            name_anime (str): Término de búsqueda para encontrar animes
            pagina (int): Número de página para paginación (empezando en 0)

        Returns:
            SearchResponse: Resultados de la búsqueda estructurados

        Raises:
            AnimeException: Si hay errores en los parámetros o la búsqueda
        """
        self._logger.info(f"Buscando anime: '{name_anime}' - Página: {pagina}")
        try:
            result = self.scraper.search(name_anime=name_anime, pagina=pagina)
            self._logger.debug(f"Búsqueda completada exitosamente")
            return result
        except Exception as e:
            self._logger.error(f"Error en búsqueda: {e}")
            raise

    def anime_info(self, anime_id: str) -> AnimeInfo:
        """
        Obtiene información detallada de un anime específico.

        Args:
            anime_id (str): ID único del anime en AnimeFLV

        Returns:
            AnimeInfo: Información completa del anime (descripción, episodios, géneros, etc.)

        Raises:
            AnimeException: Si el anime_id es inválido o no se encuentra
        """
        self._logger.info(f"Obteniendo información del anime: {anime_id}")
        try:
            result = self.scraper.get_anime_info(anime_id=anime_id)
            self._logger.debug(f"Información obtenida exitosamente para: {anime_id}")
            return result
        except Exception as e:
            self._logger.error(f"Error obteniendo info de {anime_id}: {e}")
            raise

    def latest_anime(self) -> List[LatestAnime]:
        """
        Obtiene la lista de animes más recientes.

        Returns:
            List[LatestAnime]: Lista de animes recién agregados con información básica

        Raises:
            AnimeException: Si hay problemas de conectividad o procesamiento
        """
        self._logger.info("Obteniendo animes más recientes")
        try:
            result = self.scraper.get_latest_animes()
            self._logger.debug(f"Obtenidos {len(result)} animes recientes")
            return result
        except Exception as e:
            self._logger.error(f"Error obteniendo animes recientes: {e}")
            raise

    def latest_episodes(self) -> List[LatestEpisodes]:
        """
        Obtiene la lista de episodios más recientes.

        Returns:
            List[LatestEpisodes]: Lista de episodios recién publicados

        Raises:
            AnimeException: Si hay problemas de conectividad o procesamiento
        """
        self._logger.info("Obteniendo episodios más recientes")
        try:
            result = self.scraper.get_latest_episodes()
            self._logger.debug(f"Obtenidos {len(result)} episodios recientes")
            return result
        except Exception as e:
            self._logger.error(f"Error obteniendo episodios recientes: {e}")
            raise

    def links(self, anime_id: str, episodio: str) -> List[Links]:
        """
        Obtiene los enlaces de reproducción para un episodio específico.

        Args:
            anime_id (str): ID único del anime
            episodio (str): Número del episodio

        Returns:
            List[Links]: Enlaces de reproducción disponibles con información de servidores

        Raises:
            AnimeException: Si los parámetros son inválidos o no se encuentran enlaces
        """
        self._logger.info(f"Obteniendo enlaces para: {anime_id} - Episodio: {episodio}")
        try:
            result = self.scraper.get_links(anime_id=anime_id, episode=episodio)
            self._logger.debug(
                f"Obtenidos {len(result)} enlaces para {anime_id}-{episodio}"
            )
            return result
        except Exception as e:
            self._logger.error(
                f"Error obteniendo enlaces para {anime_id}-{episodio}: {e}"
            )
            raise

    def close(self) -> None:
        """
        Cierra y limpia los recursos del servicio.

        Libera la conexión del scraper y limpia la memoria.
        Útil para limpieza manual cuando el servicio ya no se necesite.
        """
        if self._scraper is not None:
            try:
                self._scraper.__exit__(None, None, None)
                self._logger.debug("Scraper cerrado correctamente")
            except Exception as e:
                self._logger.warning(f"Error al cerrar scraper: {e}")
            finally:
                self._scraper = None

    def __del__(self):
        """
        Destructor que asegura la limpieza de recursos al eliminar la instancia.
        """
        self.close()

    # Opcional: Support para context manager si el usuario lo prefiere
    def __enter__(self) -> "AnimeFLVServices":
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Context manager exit point."""
        self.close()

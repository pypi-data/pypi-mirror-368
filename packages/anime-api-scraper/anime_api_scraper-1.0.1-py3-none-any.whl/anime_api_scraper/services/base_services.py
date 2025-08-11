from abc import ABC, abstractmethod
from typing import List, Optional, Any
import logging
from anime_api_scraper.models.data_models import (
    SearchResponse,
    AnimeInfo,
    LatestAnime,
    LatestEpisodes,
    Links,
)


class BaseServices(ABC):
    """
    Clase base abstracta para servicios de anime.

    Define la interfaz común que deben implementar todos los servicios
    de diferentes proveedores de anime (AnimeFLV, Crunchyroll, etc.).
    Proporciona funcionalidades base como logging y gestión de recursos.
    """

    def __init__(self):
        """
        Inicializa el servicio base.

        Configura el logger y establece el estado inicial del scraper.
        Las clases hijas deben llamar super().__init__() en su constructor.
        """
        self._scraper: Optional[Any] = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f"Inicializando servicio: {self.__class__.__name__}")

    @property
    @abstractmethod
    def scraper(self) -> Any:
        """
        Obtiene el scraper específico del proveedor.

        Las clases hijas deben implementar este método para proporcionar
        su scraper específico con lazy loading.

        Returns:
            Any: Instancia del scraper configurada y lista para usar
        """
        pass

    @abstractmethod
    def search_anime(self, name_anime: str = "", pagina: int = 0) -> SearchResponse:
        """
        Realiza una búsqueda de animes.

        Args:
            name_anime (str): Término de búsqueda para encontrar animes
            pagina (int): Número de página para paginación (empezando en 0)

        Returns:
            SearchResponse: Resultados de la búsqueda estructurados

        Raises:
            AnimeException: Si hay errores en los parámetros o la búsqueda
        """
        pass

    @abstractmethod
    def anime_info(self, anime_id: str) -> AnimeInfo:
        """
        Obtiene información detallada de un anime específico.

        Args:
            anime_id (str): ID único del anime en el proveedor

        Returns:
            AnimeInfo: Información completa del anime

        Raises:
            AnimeException: Si el anime_id es inválido o no se encuentra
        """
        pass

    @abstractmethod
    def latest_anime(self) -> List[LatestAnime]:
        """
        Obtiene la lista de animes más recientes.

        Returns:
            List[LatestAnime]: Lista de animes recién agregados

        Raises:
            AnimeException: Si hay problemas de conectividad o procesamiento
        """
        pass

    @abstractmethod
    def latest_episodes(self) -> List[LatestEpisodes]:
        """
        Obtiene la lista de episodios más recientes.

        Returns:
            List[LatestEpisodes]: Lista de episodios recién publicados

        Raises:
            AnimeException: Si hay problemas de conectividad o procesamiento
        """
        pass

    @abstractmethod
    def links(self, anime_id: str, episodio: str) -> List[Links]:
        """
        Obtiene los enlaces de reproducción para un episodio específico.

        Args:
            anime_id (str): ID único del anime
            episodio (str): Número del episodio

        Returns:
            List[Links]: Enlaces de reproducción disponibles

        Raises:
            AnimeException: Si los parámetros son inválidos o no se encuentran enlaces
        """
        pass

    def close(self) -> None:
        """
        Cierra y limpia los recursos del servicio.

        Método base que puede ser sobrescrito por las clases hijas
        para implementar limpieza específica del proveedor.
        """
        if self._scraper is not None:
            try:
                # Intentar cerrar usando context manager si está disponible
                if hasattr(self._scraper, "__exit__"):
                    self._scraper.__exit__(None, None, None)
                    self._logger.debug("Scraper cerrado usando context manager")
                # O usar método close si está disponible
                elif hasattr(self._scraper, "close"):
                    self._scraper.close()
                    self._logger.debug("Scraper cerrado usando método close")
                else:
                    self._logger.debug("Scraper no requiere limpieza específica")
            except Exception as e:
                self._logger.warning(f"Error al cerrar scraper: {e}")
            finally:
                self._scraper = None
                self._logger.debug("Referencia del scraper limpiada")

    def _log_operation(self, operation: str, **kwargs) -> None:
        """
        Registra información sobre una operación.

        Método de utilidad para que las clases hijas registren
        operaciones de forma consistente.

        Args:
            operation (str): Nombre de la operación
            **kwargs: Parámetros adicionales a incluir en el log
        """
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self._logger.info(
            f"Ejecutando {operation}" + (f" - {params}" if params else "")
        )

    def _log_result(self, operation: str, result: Any) -> None:
        """
        Registra el resultado de una operación.

        Args:
            operation (str): Nombre de la operación
            result (Any): Resultado obtenido
        """
        if isinstance(result, list):
            self._logger.debug(
                f"{operation} completado - {len(result)} elementos obtenidos"
            )
        else:
            self._logger.debug(f"{operation} completado exitosamente")

    def _log_error(self, operation: str, error: Exception) -> None:
        """
        Registra errores de operaciones.

        Args:
            operation (str): Nombre de la operación que falló
            error (Exception): Excepción ocurrida
        """
        self._logger.error(f"Error en {operation}: {error}")

    def __del__(self):
        """
        Destructor que asegura la limpieza de recursos.
        """
        try:
            self.close()
        except Exception as e:
            # Evitar excepciones en el destructor
            pass

    # Support opcional para context manager
    def __enter__(self) -> "BaseServices":
        """
        Context manager entry point.

        Returns:
            BaseServices: La instancia actual del servicio
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Context manager exit point.

        Args:
            exc_type: Tipo de excepción (si ocurrió alguna)
            exc_value: Valor de la excepción (si ocurrió alguna)
            traceback: Objeto traceback (si ocurrió alguna excepción)
        """
        self.close()

    def __repr__(self) -> str:
        """
        Representación string del servicio.

        Returns:
            str: Representación del servicio
        """
        return f"{self.__class__.__name__}(scraper_loaded={self._scraper is not None})"

import cloudscraper
from .base_scraper import BaseScraper
from urllib.parse import urlencode
from typing import List
from anime_api_scraper.utils.exception import AnimeException
from anime_api_scraper.processors.animeflv_processors import AnimeFLVProcessors
from anime_api_scraper.models.data_models import (
    AnimeInfo,
    SearchResponse,
    LatestAnime,
    LatestEpisodes,
    Links,
)


class AnimeFLVScraper(BaseScraper):
    """
    Scraper especializado para extraer información de animes desde AnimeFlv.

    Esta clase maneja todas las operaciones de scraping web para el sitio AnimeFlv,
    incluyendo búsquedas, obtención de información detallada y listado de animes recientes.
    Utiliza cloudscraper para evitar protecciones anti-bot y procesadores especializados
    para extraer y estructurar los datos.
    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa el scraper de AnimeFlv con configuración específica del sitio.
        Establece las URLs base necesarias y crea una instancia de cloudscraper
        para realizar las peticiones HTTP evitando detección de bot.

        Args:
            *args: Argumentos posicionales pasados al constructor padre
            **kwargs: Argumentos de palabra clave pasados al constructor padre
        """
        super().__init__(*args, **kwargs)
        self._base_url = "https://animeflv.net"
        self._search_url = "https://animeflv.net/browse"
        self._anime_info_url = "https://animeflv.net/anime/"
        self.ver_anime = "https://animeflv.net/ver/"
        self._scraper = cloudscraper.create_scraper()
        self._soup = AnimeFLVProcessors()

    def __enter__(self) -> "AnimeFLVScraper":
        """
        Implementa el protocolo de context manager para entrada.
        Permite usar el scraper con la declaración 'with' para manejo
        automático de recursos y limpieza al finalizar.

        Returns:
            AnimeFLVScraper: Instancia actual del scraper configurada
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Implementa el protocolo de context manager para salida.
        Limpia los recursos utilizados cerrando la sesión del scraper
        al finalizar el bloque 'with'.

        Args:
            exc_type: Tipo de excepción (si ocurrió alguna)
            exc_value: Valor de la excepción (si ocurrió alguna)
            traceback: Objeto traceback (si ocurrió alguna excepción)
        """
        self._scraper.close()

    def search(self, name_anime: str = "", pagina: int = 0) -> SearchResponse:
        """
        Realiza búsquedas de animes por nombre en el sitio AnimeFlv.
        Construye la URL de búsqueda con los parámetros especificados,
        ejecuta la petición HTTP y procesa los resultados encontrados.

        Args:
            name_anime: Nombre o término de búsqueda del anime
            pagina: Número de página para paginación (0 para primera página)

        Returns:
            SearchResponse: Objeto con resultados de la búsqueda estructurados

        Raises:
            AnimeException: Si el nombre del anime está vacío o la página
                           no es un número entero válido
        """
        if not name_anime:
            raise AnimeException(
                message="el nombre del anime no puede estar vacío.",
                metodo="search",
                source="animeflv",
            )
        if not isinstance(pagina, int):
            raise AnimeException(
                message="la página debe ser un número entero",
                metodo="search",
                source="animeflv",
            )
        params = dict()
        params["q"] = name_anime
        if pagina > 1:
            params["page"] = pagina
        query = urlencode(params)
        request_url = f"{self._search_url}?{query}"
        response = self._scraper.get(request_url)
        soup = self._soup.process_search(response)
        return soup

    def get_anime_info(self, anime_id: str) -> AnimeInfo:
        """
        Obtiene información detallada de un anime específico usando su ID.
        Accede a la página individual del anime y extrae toda la información
        disponible como descripción, episodios, géneros y metadatos.

        Args:
            anime_id: ID único del anime en el formato usado por AnimeFlv

        Returns:
            AnimeInfo: Objeto con información completa del anime estructurada

        Raises:
            AnimeException: Si el anime_id está vacío o es inválido
        """
        if not anime_id:
            raise AnimeException(
                message="el id del anime no puede estar vacio",
                metodo="get_anime_info",
                source="animeflv",
            )
        request_url = f"{self._anime_info_url}{anime_id}"
        response = self._scraper.get(request_url)
        soup = self._soup.process_anime_info(response, anime_id)
        return soup

    def get_latest_animes(self) -> List[LatestAnime]:
        """
        Obtiene la lista de animes más recientes desde la página principal.
        Accede a la página principal de AnimeFlv y extrae información
        de todos los animes recién agregados o actualizados.

        Returns:
            List[LatestAnime]: Lista de objetos con información básica de animes recientes:
                - ID, nombre, tipo, puntuación, descripción e imagen

        Raises:
            AnimeException: Si no se pueden obtener animes recientes o hay
                           problemas de conectividad con el sitio
        """
        response = self._scraper.get(self._base_url)
        soup = self._soup.process_latest_animes(response)
        return soup

    def get_latest_episodes(self) -> List[LatestEpisodes]:
        """
        Obtiene la lista de episodios más recientes desde la página principal.
        Accede a la página principal de AnimeFlv y extrae información de todos los
        episodios recién publicados o actualizados de diferentes series de anime.

        Returns:
            List[LatestEpisodes]: Lista de objetos con información de episodios recientes:
                - ID del anime, nombre del anime, número de episodio,
                título del episodio, fecha de publicación e imagen de portada

        Raises:
            AnimeException: Si no se pueden obtener episodios recientes o hay
                        problemas de conectividad con el sitio
        """
        response = self._scraper.get(self._base_url)
        soup = self._soup.process_latest_episodes(response)
        return soup

    def get_links(self, anime_id: str, episode: str) -> List[Links]:
        """
        Obtiene los enlaces de reproducción disponibles para un episodio específico de anime.
        Accede a la página del episodio en AnimeFlv y extrae todos los servidores de video
        disponibles junto con sus URLs de reproducción, información de publicidad y compatibilidad móvil.

        Args:
            anime_id (str): Identificador único del anime (ej: "one-piece-tv")
            episode (str): Número del episodio a obtener (ej: "1", "150")

        Returns:
            List[Links]: Lista de objetos con información de enlaces de reproducción:
                - Servidor de video, título del servidor, URL de reproducción,
                nivel de anuncios, compatibilidad móvil y código de embed

        Raises:
            AnimeException: Si el anime_id está vacío, el episodio está vacío,
                            no se pueden obtener los enlaces o hay problemas
                            de conectividad con el sitio
        """
        if not anime_id:
            raise AnimeException(
                message="el id del anime no puede estar vacio",
                metodo="get_links",
                source="animeflv",
            )

        if not episode:
            raise AnimeException(
                message="el episodio no puede estar vacio",
                metodo="get_links",
                source="animeflv",
            )

        url = f"{self.ver_anime}{anime_id}-{episode}"
        response = self._scraper.get(url)
        soup = self._soup.process_links(response)
        return soup

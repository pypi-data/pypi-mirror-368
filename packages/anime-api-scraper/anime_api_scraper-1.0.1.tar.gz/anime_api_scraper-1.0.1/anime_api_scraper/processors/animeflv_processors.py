from bs4.element import ResultSet
from requests import Response
from bs4 import BeautifulSoup, Tag
from typing import Optional, Dict, List
from datetime import datetime

from .base_processors import BaseProcessors
from anime_api_scraper.models.data_models import (
    AnimeSearchResult,
    PageInfo,
    SearchResponse,
    AnimeInfo,
    AnimeRelacionado,
    LatestAnime,
    LatestEpisodes,
    Links,
)
from anime_api_scraper.utils.exception import AnimeException


class AnimeFLVProcessors(BaseProcessors):
    """
    Procesador especializado para extraer información de animes desde AnimeFlv.

    Maneja el parsing de páginas HTML y extracción de datos específicos
    del formato utilizado por AnimeFlv.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self) -> "AnimeFLVProcessors":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def _process_id_info(self, anime) -> Optional[str]:
        """
        Extrae el ID único del anime desde el elemento HTML.

        Busca el enlace del anime y extrae el identificador desde la URL.

        Args:
            anime: Elemento BeautifulSoup que contiene la información del anime

        Returns:
            str: ID del anime o None si no se encuentra
        """
        anime_id = anime.select_one("a")
        if not anime_id:
            return None
        anime_id = anime_id["href"]
        if not anime_id:
            return None
        anime_id = anime_id.split("/")[2]
        return anime_id

    def _process_name_info(self, anime) -> Optional[str]:
        """
        Extrae el nombre del anime desde el elemento HTML.

        Busca el elemento h3 que contiene el título del anime.

        Args:
            anime: Elemento BeautifulSoup que contiene la información del anime

        Returns:
            str: Nombre del anime o None si no se encuentra
        """
        nombre = anime.h3
        if not nombre:
            return None
        nombre = nombre.get_text(strip=True)
        return nombre

    def _process_page_info(self, pagination_elements) -> Optional[PageInfo]:
        """
        Procesa la información de paginación de los resultados de búsqueda.

        Extrae la página actual y el número total de páginas disponibles
        desde los elementos de paginación.

        Args:
            pagination_elements: Lista de elementos de paginación

        Returns:
            PageInfo: Objeto con información de página actual y total
        """
        if not pagination_elements:
            return PageInfo(pagina_actual=1, pagina_total=1)

        pagination = pagination_elements[0]
        page_actual = pagination.select_one("li.active a")
        if not page_actual:
            return PageInfo(pagina_actual=1, pagina_total=1)
        page_actual = page_actual.get_text(strip=True)

        page_links = pagination.select("li a[href*='page=']")
        page_numbers = []
        for link in page_links:
            page_number = link.get("href")
            if not page_number:
                return PageInfo(pagina_actual=page_actual, pagina_total=1)
            page_number = page_number.split("page=")[-1]
            page_numbers.append(int(page_number))

        page_info = PageInfo(
            pagina_actual=int(page_actual),
            pagina_total=max(page_numbers),
        )

        return page_info

    def _process_image_info(self, anime) -> Optional[str]:
        """
        Extrae la URL de la imagen/poster del anime.

        Busca el elemento img y obtiene su atributo src.

        Args:
            anime: Elemento BeautifulSoup que contiene la información del anime

        Returns:
            str: URL de la imagen o None si no se encuentra
        """
        imagen = anime.select_one("img")
        if not imagen:
            return None
        imagen = imagen["src"]
        return imagen

    def _process_single_anime(self, anime) -> AnimeSearchResult:
        """
        Procesa un único elemento de anime desde los resultados de búsqueda.

        Extrae toda la información básica necesaria para crear un objeto
        AnimeSearchResult.

        Args:
            anime: Elemento BeautifulSoup que contiene la información del anime

        Returns:
            AnimeSearchResult: Objeto con la información básica del anime

        Raises:
            ValueError: Si no se puede obtener información crítica del anime
        """
        anime_id = self._process_id_info(anime)
        if not anime_id:
            raise ValueError("No se pudo obtener el ID del anime.")

        nombre = self._process_name_info(anime)
        if not nombre:
            raise ValueError("No se pudo obtener el nombre del anime.")

        imagen = self._process_image_info(anime)
        if not imagen:
            raise ValueError("No se pudo obtener la imagen del anime.")

        anime_info = AnimeSearchResult(anime_id=anime_id, nombre=nombre, imagen=imagen)
        return anime_info

    def process_search(self, response: Response) -> SearchResponse:
        """
        Procesa la respuesta completa de una búsqueda de animes.

        Extrae todos los animes encontrados y la información de paginación
        desde la página HTML de resultados.

        Args:
            response: Respuesta HTTP de la búsqueda

        Returns:
            SearchResponse: Diccionario con resultados y información de paginación

        Raises:
            ValueError: Si no se encuentran resultados en la búsqueda
        """
        soup = BeautifulSoup(response.text, "lxml")
        result = list()
        animes = soup.select("div.Container ul.ListAnimes li article")
        pages = soup.select("div.Container div.NvCnAnm ul")
        pagination = self._process_page_info(pages)
        if not animes:
            raise ValueError("No se encontraron resultados en la búsqueda.")
        for anime in animes:
            result.append(self._process_single_anime(anime))
        if not pagination:
            pagination = PageInfo(pagina_actual=1, pagina_total=1)
        return {"results": result, "pagination": pagination}

    def _procces_anime_title(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """
        Extrae el título y tipo del anime desde la página de información.

        Busca los elementos h1.Title y span.Type para obtener el nombre
        y clasificación del anime.

        Args:
            soup: Objeto BeautifulSoup de la página del anime

        Returns:
            dict: Diccionario con 'title' y 'type' o None si no se encuentra
        """
        title = soup.select_one("h1.Title")
        if not title:
            return None
        type_anime = soup.select_one("span.Type")
        if not type_anime:
            return None
        type_anime = type_anime.get_text(strip=True)
        title = title.get_text(strip=True)
        return {"title": title, "type": type_anime}

    def _procces_related_anime(
        self, sipnopsis: ResultSet
    ) -> Optional[List[AnimeRelacionado]]:
        """
        Extrae la lista de animes relacionados desde la sección de sinopsis.

        Busca los enlaces de animes relacionados en la lista ul.ListAnmRel
        y extrae sus IDs y nombres.

        Args:
            sipnopsis: ResultSet con la sección de sinopsis del anime

        Returns:
            AnimeRelacionado: Lista de objetos AnimeRelacionado con ID y nombre
        """
        anime_rela = sipnopsis[0].select("ul.ListAnmRel li a")
        animes_relacionados = []
        if not anime_rela:
            return None
        for anime in anime_rela:
            anime_id = anime.get("href")
            if not anime_id:
                continue
            if not isinstance(anime_id, str):
                continue
            anime_id = anime_id.split("/")[2]
            anime = anime.get_text(strip=True)
            animes_relacionados.append(
                AnimeRelacionado(anime_id=anime_id, nombre=anime)
            )
        if not animes_relacionados:
            return None

        return animes_relacionados

    def _procces_episodes(self, soup: BeautifulSoup):
        """
        Extrae los episodios del JavaScript embebido en la página.

        Busca las variables 'episodes' y 'anime_info' en los script tags
        para obtener la lista de episodios y fecha del próximo episodio.

        Args:
            soup: Objeto BeautifulSoup de la página del anime

        Returns:
            dict: Diccionario con 'episodios' y 'proximo_episodio'
        """
        import re
        import json

        script_tags = soup.find_all("script")
        episodes = []
        proximo_episodio = None
        formato = "%Y-%m-%d"  # Formato de fecha esperado, por ejemplo: "2025-08-10"

        for script in script_tags:
            if script.string:
                script_content = script.string

                # Buscar la variable episodes
                episodes_match = re.search(
                    r"var episodes = (\[\[.*?\]\]);", script_content, re.DOTALL
                )

                # Buscar la variable anime_info
                anime_info_match = re.search(
                    r"var anime_info = (\[.*?\]);", script_content
                )

                try:
                    # Procesar episodes si se encontró
                    if episodes_match:
                        episodes_str = episodes_match.group(1)
                        episodes_data = json.loads(episodes_str)

                        for episode_data in episodes_data:
                            if len(episode_data) >= 2:
                                numero = episode_data[0]
                                episodes.append(numero)

                        # Ordenar por número de episodio (ascendente)
                        episodes.sort()

                    # Procesar anime_info solo para extraer la fecha
                    if anime_info_match:
                        anime_info_str = anime_info_match.group(1)
                        anime_info_data = json.loads(anime_info_str)

                        # El cuarto elemento suele ser la fecha del próximo episodio
                        if len(anime_info_data) >= 4 and anime_info_data[3]:
                            proximo_episodio = anime_info_data[3]  # "2025-08-10"
                            proximo_episodio = datetime.strptime(
                                proximo_episodio, formato
                            ).strftime("%d-%m-%Y")

                    # Si encontramos ambos, podemos salir del loop
                    if episodes_match and anime_info_match:
                        break

                except (json.JSONDecodeError, ValueError, IndexError) as e:
                    # Si hay error en el parsing, continuar buscando en otros scripts
                    print(f"Error parsing JavaScript: {e}")
                    continue

        return {"episodios": episodes, "proximo_episodio": proximo_episodio}

    def _procces_info(self, soup: BeautifulSoup):
        """
        Extrae información general del anime desde la página de detalles.

        Obtiene descripción, géneros, animes relacionados y estado de emisión
        desde diferentes secciones de la página.

        Args:
            soup: Objeto BeautifulSoup de la página del anime

        Returns:
            dict: Diccionario con información completa del anime

        Raises:
            AnimeException: Si no se encuentra la sección de sinopsis
        """
        sipnopsis = soup.select("div.Container main section.WdgtCn")
        if not sipnopsis:
            raise AnimeException(
                message="No se pudo encontrar la sección de sinopsis.",
                metodo="anime_info",
                source="animeflv",
            )
        estado = soup.select_one("div.Container aside.SidebarA p.AnmStts span")
        genres_info = sipnopsis[0].select("nav.Nvgnrs a")

        generes = []

        for gender in genres_info:
            generes.append(gender.get_text(strip=True))
        description = sipnopsis[0].find("p")
        if not description:
            return {"description": "", "genres": generes, "related_animes": []}
        description = description.get_text(strip=True)
        anime_rela = self._procces_related_anime(sipnopsis)
        estado = estado.get_text(strip=True) if estado else None

        return {
            "description": description,
            "genres": generes,
            "related_animes": anime_rela,
            "estado": estado,
            "sipnopsis": sipnopsis,
        }

    def _procces_single_anime_info(self, soup: BeautifulSoup, anime_id) -> AnimeInfo:
        """
        Procesa toda la información detallada de un único anime.

        Combina información de título, detalles generales y episodios para
        crear un objeto AnimeInfo completo.

        Args:
            soup: Objeto BeautifulSoup de la página del anime
            anime_id: ID único del anime

        Returns:
            AnimeInfo: Objeto con toda la información detallada del anime
        """
        info_title = self._procces_anime_title(soup)
        info = self._procces_info(soup)
        episodes = self._procces_episodes(soup)
        animes_relacionados = self._procces_related_anime(info["sipnopsis"])
        anime_info = AnimeInfo(
            anime_id=anime_id,
            nombre=info_title["title"] if info_title else "",
            tipo=info_title["type"] if info_title else "",
            genero=", ".join(info["genres"]) if info["genres"] else "",
            descripcion=info["description"] if info["description"] else "",
            animes_relacionados=animes_relacionados if animes_relacionados else [],
            episodios=episodes["episodios"]
            if episodes and "episodios" in episodes
            else [],
            estado=info["estado"] if info["estado"] else "",
            proximo_episodio=episodes["proximo_episodio"]
            if episodes and "proximo_episodio" in episodes
            else None,
        )
        return anime_info

    def process_anime_info(self, response: Response, anime_id: str) -> AnimeInfo:
        """
        Procesa la respuesta HTTP completa para obtener información detallada del anime.

        Método principal que coordina la extracción de toda la información
        desde la página de detalles del anime.

        Args:
            response: Respuesta HTTP de la página del anime
            anime_id: ID único del anime

        Returns:
            AnimeInfo: Objeto con información completa del anime
        """
        soup = BeautifulSoup(response.text, "lxml")
        info = self._procces_single_anime_info(soup, anime_id)
        return info

    def _process_info_lates_anime(
        self, anime: Tag
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Extrae información específica de un anime desde un elemento HTML.
        Procesa la descripción, puntuación con estrellas y tipo de anime
        desde los elementos <p> del contenedor del anime.

        Args:
            anime: Elemento Tag de BeautifulSoup que representa el contenedor del anime

        Returns:
            Optional[Dict[str, Optional[str]]]: Diccionario con la información extraída:
                - description: Texto descriptivo del anime
                - stars: Puntuación en estrellas (como string)
                - type: Tipo de anime (TV, Movie, OVA, etc.)
            Retorna None si no se encuentran elementos <p>
        """
        info = anime.find_all("p")
        if not info:
            return None
        description = info[1].get_text(strip=True)
        stars = None
        if len(info) > 0:
            star_element = info[0].find("span", class_="Vts fa-star")
            if star_element:
                stars = star_element.get_text(strip=True)
        anime_type = None
        if len(info) > 0:
            type_element = info[0].find("span", class_="Type tv")
            if type_element:
                anime_type = type_element.get_text(strip=True)
        return {"description": description, "stars": stars, "type": anime_type}

    def _process_single_lates_anime(self, animes: ResultSet) -> list[LatestAnime]:
        """
        Procesa una colección de elementos HTML para convertirlos en objetos LatestAnime.
        Método que itera sobre cada anime encontrado y extrae toda su información
        utilizando los métodos auxiliares de procesamiento.

        Args:
            animes: ResultSet de BeautifulSoup con elementos HTML de animes

        Returns:
            list[LatestAnime]: Lista de objetos LatestAnime con información completa:
                - anime_id: ID único del anime
                - nombre: Nombre del anime
                - tipo: Tipo de anime (TV, Movie, etc.)
                - puntaje: Puntuación convertida a float
                - descripción: Descripción del anime
                - imagen: URL de la imagen del anime
        """
        animes_list = []
        for anime in animes:
            id_anime = self._process_id_info(anime)
            imagen = self._process_image_info(anime)
            nombre = self._process_name_info(anime)
            info = self._process_info_lates_anime(anime)
            descripcion = info["description"] if info else ""
            stars = float(info["stars"]) if info else None
            type_anime = info["type"] if info else None
            animes_list.append(
                LatestAnime(
                    anime_id=id_anime,
                    nombre=nombre,
                    tipo=type_anime,
                    puntaje=stars,
                    descripción=descripcion,
                    imagen=imagen,
                )
            )
        return animes_list

    def process_latest_animes(self, response: Response) -> List[LatestAnime]:
        """
        Procesa la respuesta HTTP completa para obtener la lista de animes más recientes.
        Método principal que coordina la extracción de todos los animes recientes
        desde la página principal de AnimeFlv utilizando selectores CSS.

        Args:
            response: Respuesta HTTP de la página principal de animes recientes

        Returns:
            List[LatestAnime]: Lista de objetos LatestAnime con información completa

        Raises:
            AnimeException: Si no se encuentran animes recientes en la página,
                        con detalles del método y fuente que causó el error
        """
        soup = BeautifulSoup(response.text, "lxml")
        list_animes = soup.select("div.Container main.Main ul.ListAnimes li")
        if not list_animes:
            raise AnimeException(
                message="No se encontraron animes recientes.",
                metodo="latest_animes",
                source="animeflv",
            )
        animes = self._process_single_lates_anime(list_animes)
        return animes

    def _process_tittle_last_episode(self, episode: ResultSet) -> Optional[str]:
        """
        Extrae el título del anime desde un elemento HTML de episodio.
        Busca el elemento <strong> dentro del contenedor del episodio
        que contiene el nombre del anime al que pertenece el episodio.

        Args:
            episode: Elemento ResultSet de BeautifulSoup que representa el contenedor del episodio

        Returns:
            Optional[str]: Título del anime o None si no se encuentra el elemento
        """
        tittle = episode.select_one("strong")
        tittle = tittle.get_text(strip=True) if tittle else None
        return tittle

    def _process_num_episode(self, episode):
        """
        Extrae el número del episodio desde un elemento HTML.
        Busca el elemento con clase 'Capi' que contiene la numeración
        específica del episodio dentro de la serie.

        Args:
            episode: Elemento HTML que representa el contenedor del episodio

        Returns:
            Optional[str]: Número del episodio como string o None si no se encuentra
        """
        episode_num = episode.select_one("span.Capi")
        episode_num = episode_num.get_text(strip=True) if episode_num else None
        return episode_num

    def _process_single_latest_episode(
        self, episodes: ResultSet
    ) -> List[LatestEpisodes]:
        """
        Procesa una colección de elementos HTML para convertirlos en objetos LatestEpisodes.
        Método que itera sobre cada episodio encontrado y extrae toda su información
        utilizando los métodos auxiliares de procesamiento específicos para episodios.

        Args:
            episodes: ResultSet de BeautifulSoup con elementos HTML de episodios recientes

        Returns:
            List[LatestEpisodes]: Lista de objetos LatestEpisodes con información completa:
                - anime_id: ID único del anime
                - nombre: Título del anime al que pertenece el episodio
                - episodio: Número del episodio
                - imagen: URL de la imagen de portada del episodio
        """
        anime_list = []
        for episode in episodes:
            id_anime = self._process_id_info(episode)
            tittle = self._process_tittle_last_episode(episode)
            episode_num = self._process_num_episode(episode)
            imagen = self._process_image_info(episode)
            anime_list.append(
                LatestEpisodes(
                    anime_id=id_anime,
                    nombre=tittle,
                    episodio=episode_num,
                    imagen=imagen,
                )
            )
        return anime_list

    def process_latest_episodes(self, response: Response) -> List[LatestEpisodes]:
        """
        Procesa la respuesta HTTP completa para obtener la lista de episodios más recientes.
        Método principal que coordina la extracción de todos los episodios recientes
        desde la página principal de AnimeFlv utilizando selectores CSS específicos.

        Args:
            response: Respuesta HTTP de la página principal con episodios recientes

        Returns:
            List[LatestEpisodes]: Lista de objetos LatestEpisodes con información completa

        Raises:
            AnimeException: Si no se encuentran episodios recientes en la página,
                        con detalles del método y fuente que causó el error
        """
        soup = BeautifulSoup(response.text, "lxml")
        list_episodes = soup.select("div.Container main.Main ul.ListEpisodios li")
        if not list_episodes:
            raise AnimeException(
                message="No se encontraron episodios recientes.",
                metodo="latest_episodes",
                source="animeflv",
            )
        episodes = self._process_single_latest_episode(list_episodes)
        return episodes

    def _process_get_links(self, scripts: ResultSet) -> List[Links]:
        """
        Procesa los scripts JavaScript para extraer enlaces de reproducción de video.
        Busca en todos los tags <script> la variable 'videos' que contiene la información
        de los servidores disponibles y extrae los datos de cada servidor de streaming.

        Args:
            scripts (ResultSet): Colección de tags <script> obtenidos del HTML de la página

        Returns:
            List[Links]: Lista de objetos con información de enlaces de reproducción:
                - Servidor de video, título del servidor y URL de reproducción

        Note:
            Maneja errores de parsing JSON silenciosamente continuando con el siguiente script
            si encuentra contenido malformado o datos faltantes
        """
        import re
        import json

        links = []
        for script in scripts:
            if script.string:
                script_content = script.string
                link_match = re.search(r"var videos = (\{.*?\});", script_content)
                try:
                    if link_match:
                        links_str = link_match.group(1)
                        links_data = json.loads(links_str)
                        links_data = links_data["SUB"]
                        for link_data in links_data:
                            server = link_data.get("server", "Desconocido")
                            title = link_data.get("title", "Sin título")
                            code = link_data.get("code", "")
                            links.append(
                                {
                                    "server": server,
                                    "titulo": title,
                                    "url": code,
                                }
                            )
                except (json.JSONDecodeError, ValueError, IndexError) as e:
                    print(f"Error parsing links JavaScript: {e}")
                    continue
        return links

    def process_links(self, response: Response) -> List[Links]:
        """
        Extrae y procesa todos los enlaces de reproducción disponibles desde la respuesta HTTP.
        Analiza el contenido HTML de la página del episodio, localiza todos los scripts
        JavaScript y extrae la información de servidores de video disponibles.

        Args:
            response (Response): Objeto Response con el contenido HTML de la página del episodio

        Returns:
            List[Links]: Lista de objetos con información de enlaces de reproducción:
                - Servidor de video, título del servidor y URL de reproducción

        Raises:
            AnimeException: Si no se encuentran tags <script> en el HTML de la página,
                            lo que indica problemas con la estructura de la página
                            o contenido bloqueado
        """
        soup = BeautifulSoup(response.text, "lxml")
        script_tags = soup.find_all("script")
        links = self._process_get_links(script_tags)
        if not script_tags:
            raise AnimeException(
                message="No se encontraron enlaces de streaming.",
                metodo="get_links",
                source="animeflv",
            )
        return links

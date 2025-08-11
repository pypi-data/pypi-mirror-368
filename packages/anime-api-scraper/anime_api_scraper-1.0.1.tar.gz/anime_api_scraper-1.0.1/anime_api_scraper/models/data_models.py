from dataclasses import dataclass
from typing import List, Optional, TypedDict


@dataclass()
class AnimeRelacionado:
    anime_id: str
    nombre: str


@dataclass()
class AnimeInfo:
    anime_id: str
    nombre: str
    tipo: str
    genero: str
    descripcion: str
    animes_relacionados: Optional[List[AnimeRelacionado]]
    episodios: List[str]
    estado: str
    proximo_episodio: Optional[str] = None


@dataclass()
class AnimeSearchResult:
    anime_id: str
    nombre: str
    imagen: Optional[str] = None


@dataclass()
class PageInfo:
    pagina_actual: int
    pagina_total: int


class SearchResponse(TypedDict):
    results: list[AnimeSearchResult]
    pagination: PageInfo


@dataclass()
class LatestAnime:
    anime_id: Optional[str] = None
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    puntaje: Optional[float] = None
    descripción: Optional[str] = None
    imagen: Optional[str] = None


@dataclass()
class LatestEpisodes:
    anime_id: Optional[str] = None
    nombre: Optional[str] = None
    episodio: Optional[str] = None
    imagen: Optional[str] = None


@dataclass()
class Links:
    server: str
    titulo: str
    url: str

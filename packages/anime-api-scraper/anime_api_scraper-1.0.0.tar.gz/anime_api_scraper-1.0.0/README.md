# 🎌 Anime Scraper

Un scraper web robusto y escalable para extraer información de sitios de anime, comenzando con **AnimeFlv**. Este proyecto está diseñado con una arquitectura modular que permite agregar fácilmente nuevos sitios de anime en el futuro.

## 📋 Características

- 🔍 **Búsqueda de animes** por nombre con paginación
- 📊 **Información detallada** de animes (sinopsis, géneros, episodios, etc.)
- 🆕 **Animes más recientes** desde la página principal
- 📺 **Episodios recientes** con información actualizada
- 🔗 **Enlaces de reproducción** para episodios específicos
- 🛡️ **Protección anti-bot** usando cloudscraper
- 🏗️ **Arquitectura modular** para fácil extensión a nuevos sitios

## 🚀 Instalación

### Requisitos previos

- Python 3.8+
- pip (gestor de paquetes de Python)

### Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `beautifulsoup4` - Parsing HTML
- `cloudscraper` - Evadir protecciones anti-bot
- `requests` - Peticiones HTTP
- `lxml` - Parser XML/HTML rápido

## 📁 Estructura del Proyecto

```
anime-scraper/
├── api/
│   ├── models/
│   │   └── data_models.py          # Modelos de datos (AnimeInfo, SearchResponse, etc.)
│   ├── processors/
│   │   ├── base_processors.py      # Clase base para procesadores
│   │   └── animeflv_processors.py  # Procesador específico para AnimeFlv
│   ├── scrapers/
│   │   ├── base_scraper.py         # Clase base para scrapers
│   │   └── animeflv_scraper.py     # Scraper específico para AnimeFlv
│   └── utils/
│       └── exception.py            # Excepciones personalizadas
├── requirements.txt
└── README.md
```

## 🔧 Uso

### Inicialización del Scraper

```python
from api.scrapers.animeflv_scraper import AnimeFLVScraper

# Usando context manager (recomendado)
with AnimeFLVScraper() as scraper:
    # Tu código aquí
    pass
```

### Búsqueda de Animes

```python
with AnimeFLVScraper() as scraper:
    # Buscar animes por nombre
    resultados = scraper.search("Naruto", pagina=1)
    
    print(f"Página {resultados['pagination'].pagina_actual} de {resultados['pagination'].pagina_total}")
    
    for anime in resultados['results']:
        print(f"ID: {anime.anime_id}")
        print(f"Nombre: {anime.nombre}")
        print(f"Imagen: {anime.imagen}")
```

### Información Detallada de un Anime

```python
with AnimeFLVScraper() as scraper:
    # Obtener información completa
    anime_info = scraper.get_anime_info("naruto-tv")
    
    print(f"Nombre: {anime_info.nombre}")
    print(f"Tipo: {anime_info.tipo}")
    print(f"Géneros: {anime_info.genero}")
    print(f"Descripción: {anime_info.descripcion}")
    print(f"Estado: {anime_info.estado}")
    print(f"Episodios disponibles: {len(anime_info.episodios)}")
    
    if anime_info.proximo_episodio:
        print(f"Próximo episodio: {anime_info.proximo_episodio}")
    
    # Animes relacionados
    for relacionado in anime_info.animes_relacionados:
        print(f"- {relacionado.nombre} (ID: {relacionado.anime_id})")
```

### Animes y Episodios Recientes

```python
with AnimeFLVScraper() as scraper:
    # Obtener animes más recientes
    animes_recientes = scraper.get_latest_animes()
    
    for anime in animes_recientes:
        print(f"{anime.nombre} - {anime.tipo} - ⭐{anime.puntaje}")
    
    # Obtener episodios más recientes
    episodios_recientes = scraper.get_latest_episodes()
    
    for episodio in episodios_recientes:
        print(f"{episodio.nombre} - Episodio {episodio.episodio}")
```

### Enlaces de Reproducción

```python
with AnimeFLVScraper() as scraper:
    # Obtener enlaces para un episodio específico
    enlaces = scraper.get_links("naruto-tv", "1")
    
    for enlace in enlaces:
        print(f"Servidor: {enlace['server']}")
        print(f"Título: {enlace['titulo']}")
        print(f"URL: {enlace['url']}")
```

## 📊 Modelos de Datos

### AnimeSearchResult
Información básica para resultados de búsqueda:
- `anime_id`: Identificador único
- `nombre`: Título del anime
- `imagen`: URL de la imagen de portada

### AnimeInfo
Información completa del anime:
- `anime_id`: Identificador único
- `nombre`: Título completo
- `tipo`: Tipo (TV, Movie, OVA, etc.)
- `genero`: Géneros separados por comas
- `descripcion`: Sinopsis del anime
- `animes_relacionados`: Lista de animes relacionados
- `episodios`: Lista de números de episodios disponibles
- `estado`: Estado de emisión (En emisión, Finalizado, etc.)
- `proximo_episodio`: Fecha del próximo episodio (si aplica)

### LatestAnime
Información de animes recientes:
- `anime_id`: Identificador único
- `nombre`: Título del anime
- `tipo`: Tipo de anime
- `puntaje`: Puntuación (rating)
- `descripción`: Descripción breve
- `imagen`: URL de la imagen

### LatestEpisodes
Información de episodios recientes:
- `anime_id`: Identificador del anime
- `nombre`: Nombre del anime
- `episodio`: Número del episodio
- `imagen`: URL de la imagen del episodio

## 🏗️ Arquitectura

### Patrón de Diseño

El proyecto utiliza una **arquitectura modular** basada en el patrón de responsabilidad única:

1. **Scrapers** (`BaseScraper` → `AnimeFLVScraper`)
   - Manejan las peticiones HTTP
   - Coordinan el flujo de scraping
   - Gestionan la sesión y configuración específica del sitio

2. **Processors** (`BaseProcessors` → `AnimeFLVProcessors`)
   - Procesan el HTML crudo
   - Extraen y estructuran los datos
   - Convierten HTML en objetos Python

3. **Models** (`data_models.py`)
   - Definen la estructura de datos
   - Validan tipos usando dataclasses
   - Proporcionan consistencia entre componentes

### Ventajas de esta Arquitectura

- ✅ **Escalabilidad**: Fácil agregar nuevos sitios
- ✅ **Mantenibilidad**: Separación clara de responsabilidades
- ✅ **Reutilización**: Componentes base reutilizables
- ✅ **Testeo**: Cada componente se puede testear independientemente

## 🔮 Extensibilidad

Para agregar un nuevo sitio de anime (ej: Crunchyroll):

1. **Crear el procesador específico**:
```python
class CrunchyrollProcessors(BaseProcessors):
    def process_search(self, response):
        # Lógica específica para Crunchyroll
        pass
```

2. **Crear el scraper específico**:
```python
class CrunchyrollScraper(BaseScraper):
    def __init__(self):
        self._base_url = "https://crunchyroll.com"
        self._processor = CrunchyrollProcessors()
```

3. **Implementar los métodos requeridos** siguiendo la interfaz base.

## ⚡ Manejo de Errores

El proyecto incluye manejo robusto de errores:

### AnimeException
Excepción personalizada que incluye:
- `message`: Descripción del error
- `metodo`: Método donde ocurrió el error
- `source`: Fuente del error (ej: "animeflv")

### Validaciones Comunes
- ✅ Validación de parámetros de entrada
- ✅ Verificación de elementos HTML existentes
- ✅ Manejo de contenido malformado
- ✅ Timeout y errores de conectividad

## 🛡️ Características Técnicas

### Anti-Bot Protection
- Utiliza `cloudscraper` para evadir protecciones Cloudflare
- Headers realistas de navegador
- Manejo automático de challenges JavaScript

### Parsing Robusto
- Múltiples selectores CSS como fallback
- Validación de datos extraídos
- Manejo graceful de contenido faltante

### Performance
- Sesión persistente para múltiples requests
- Parser `lxml` para velocidad optimizada
- Context managers para gestión eficiente de recursos

## 📝 Ejemplos Avanzados

### Búsqueda con Paginación Completa

```python
def buscar_anime_completo(nombre):
    """Busca un anime en todas las páginas disponibles."""
    with AnimeFLVScraper() as scraper:
        todos_resultados = []
        pagina = 1
        
        while True:
            resultado = scraper.search(nombre, pagina)
            todos_resultados.extend(resultado['results'])
            
            if pagina >= resultado['pagination'].pagina_total:
                break
            pagina += 1
        
        return todos_resultados
```

### Información Completa de un Anime

```python
def info_anime_completa(anime_id):
    """Obtiene toda la información disponible de un anime."""
    with AnimeFLVScraper() as scraper:
        info = scraper.get_anime_info(anime_id)
        
        # Obtener enlaces del primer episodio si está disponible
        enlaces = []
        if info.episodios:
            try:
                enlaces = scraper.get_links(anime_id, info.episodios[0])
            except Exception as e:
                print(f"No se pudieron obtener enlaces: {e}")
        
        return {
            'info': info,
            'enlaces_primer_episodio': enlaces
        }
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

### Guías para Contribuir

- Sigue el estilo de código existente
- Agrega docstrings a todas las funciones públicas
- Incluye manejo de errores apropiado
- Escribe tests para nuevas funcionalidades

## ⚠️ Consideraciones Legales

Este proyecto está diseñado para **uso educativo y personal**. Los usuarios son responsables de:

- Cumplir con los términos de servicio de los sitios web
- Respetar los derechos de autor del contenido
- Usar el scraper de manera responsable y ética
- No sobrecargar los servidores con requests excesivos

## 🐛 Resolución de Problemas

### Errores Comunes

**Error: "No se encontraron resultados"**
- Verifica que el nombre del anime esté escrito correctamente
- Algunos animes pueden tener nombres específicos en el sitio

**Error de conexión**
- Verifica tu conexión a internet
- El sitio podría estar temporalmente inaccesible
- Considera implementar reintentos automáticos

**Error: "No se pudieron obtener enlaces"**
- Verifica que el anime_id y número de episodio sean correctos
- Algunos episodios pueden no tener enlaces disponibles

## 🔄 Roadmap

### Versión Actual (v1.0)
- ✅ Scraper completo para AnimeFlv
- ✅ Búsqueda, información detallada y enlaces
- ✅ Manejo robusto de errores

### Futuras Versiones
- 📋 Soporte para múltiples sitios de anime
- 🔄 Sistema de cache para mejorar performance
- 📊 API REST para acceso programático
- 🤖 Rate limiting inteligente
- 📱 Interfaz web para uso fácil
- 🔍 Búsqueda avanzada con filtros
- 📈 Estadísticas y analytics

## 🏷️ Versionado

Utilizamos [SemVer](http://semver.org/) para el versionado. Para las versiones disponibles, revisa los [tags de este repositorio](https://github.com/tu-usuario/anime-scraper/tags).

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - revisa el archivo [LICENSE.md](LICENSE.md) para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [TuUsuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Comunidad de desarrolladores de Python
- Mantenedores de BeautifulSoup y cloudscraper
- Sitios de anime que proporcionan contenido a los fans

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de [Issues](https://github.com/tu-usuario/anime-scraper/issues)
2. Crea un nuevo issue con detalles del problema
3. Incluye información de tu entorno (Python version, OS, etc.)

---

**⚡ ¿Te gusta el proyecto?** ¡Dale una estrella ⭐ en GitHub!

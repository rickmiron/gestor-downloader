from __future__ import annotations
from bs4 import BeautifulSoup
import re
import requests
import bisect
from typing import (
    Any,
    AnyStr,
    Callable,
    Literal,
    NoReturn,
    Optional,
    Type,
    Union,
)

class Downloader:
    PRIORITY = 1
    MAX_CORE: int = 1
    MAX_PARALLEL: int = 1
    nphilo = 1
    MAX_SPEED: Optional[float] = None
    URLS: Optional[list[str|Callable[[str],bool]]] = []
    icon: Optional[str] = None
    single: bool = False
    session: Optional[Session] = None
    header: Optional[dict[str, str]] = None
    status: Literal["ready", "working", "done", "error"] = "ready"
    _subclasesdic:dict[str,type[Downloader]]={}
    _listasubclase:list[type[Downloader]]=[]
    _listasubindice=[]
    _listasubname=[]
    _recientename=['']
    _clases=set()
    _getdix:Callable[[str],str]=None
    _settitle:Callable[[str,int,bool],None]=None
    _title: Optional[str] = None
    _url=''
    addtarea:Callable[[str],None]=None

    def __init__(self):
        self._urls=[]
        self._names={}
        self.thumbnail=None
        self._tarea=None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasesdic[cls.__name__]=cls
        cls._recientename[0]=cls.__name__
    
    @classmethod
    def ordenalounico(cls):
        clx=cls._subclasesdic[cls._recientename[0]]
        if clx.__name__ in cls._clases:
            ind=cls._listasubname.index(clx.__name__)
            if cls._listasubclase[ind].PRIORITY == clx.PRIORITY:
                cls._listasubclase[ind]=clx
            else:
                cls._listasubindice.pop(ind)
                cls._listasubclase.pop(ind)
                cls._listasubname.pop(ind)
                ind=bisect.bisect_left(cls._listasubindice, clx.PRIORITY)
                cls._listasubindice.insert(ind, clx.PRIORITY)
                cls._listasubclase.insert(ind, clx)
                cls._listasubname.insert(ind, clx.__name__)
        else:
            ind=bisect.bisect_left(cls._listasubindice, clx.PRIORITY)
            cls._listasubindice.insert(ind, clx.PRIORITY)
            cls._listasubclase.insert(ind, clx)
            cls._listasubname.insert(ind, clx.__name__)
            cls._clases.add(clx.__name__)

    @classmethod
    def ordenaloinicio(cls):
        cls._listasubclase=[v for v in cls._subclasesdic.values()]
        cls._listasubclase.sort(key=lambda x: x.PRIORITY)
        for v in cls._listasubclase:
            cls._clases.add(v.__name__)
            cls._listasubindice.append(v.PRIORITY)
            cls._listasubname.append(v.__name__)
    
    @classmethod
    def encontrar_subclase_por_url(cls, url:str) -> str:
        if url:
            for subclase in cls._listasubclase:
                for u in subclase.URLS:
                    if isinstance(u, str):
                        if u in url:
                            return subclase.__name__
                    elif u(url):
                        return subclase.__name__
        return None

    @classmethod
    def encontrar_subclase_por_urldic(cls, url:str) -> str:
        if url:
            for name,subclase in cls._subclasesdic.items():
                for u in subclase.URLS:
                    if isinstance(u, str):
                        if u in url:
                            return name
                    elif u(url):
                        return name
        return None

    @classmethod
    def obtener_nombresubclases(cls)->list[str]:
        return [name for name in cls._subclasesdic]
    
    @classmethod
    def obtener_ultimonombre(cls)->str:
        return cls._recientename[0]

    @classmethod
    def obtener_subclase(cls,name:str) -> type[Downloader]:
        #return cls._subclases
        return cls._subclasesdic[name]#()

    @classmethod
    def encontrar_subclase_por_urlss(cls, url:str)-> type[Downloader]:
        for subclase in cls._subclases:
            for u in subclase.URLS:
                if u in url:
                    return subclase
        return 0
    @property
    def url(self) -> str:
        return self._url
    @url.setter
    def url(self, value: Any) -> str:
        self._url=value
    @property
    def title(self) -> str:
        return self._title
    @title.setter
    def title(self, value: Any) -> str:
        self._title=value
    @property
    def urls(self) -> list[str]:
        return self._urls
    @urls.setter
    def urls(self, value: Any):
        self._urls=value
    @property
    def filenames(self) -> dict[str, str]:
        return self._names
    @filenames.setter
    def filenames(self, value: Any):
        self._names=value
    @property
    def dir(self) -> str:
        ddd=self._getdix(self.__class__.__name__)
        if not self.single and not self.title:
            raise Exception('self.dir need self.title')
        return ddd if self.single else (ddd+'\\'+self.title)

    def Invalid(
        self, s: str = "", e: Type[BaseException] = None, fail: bool = False
    ) -> None:
        """
        Notifies the user that an exception has occurred.
        """
        ...
    def init(self) -> None:
        pass
    def read(self) -> None:
        pass
    def setTitle(self,titulo:str):
        self._tarea.titulo=titulo
        self._settitle(titulo,self._tarea.posirecta,self._tarea.cerrar)
    def on_error(self, e: Type[Exception]) -> NoReturn:
        """
        Handle error
        """
        ...
    def post_processing(self):
        pass
    def print_(self,texto:Any):
        self._tarea.descri+=str(texto)+'\n'


class Session(requests.Session):
    # Sesión base compartida entre todas las instancias
    _base_session:requests.Session = None

    @classmethod
    def set_base_session(cls, session:requests.Session):
        session.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3', 'Accept-Encoding': 'none', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Connection': 'keep-alive', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Language': 'en-US,en;q=0.8', 'Upgrade-Insecure-Requests': '1'}
        cls._base_session = session

    def __init__(self,list_pattern:list[str]=None):
        super().__init__()
        ACCEPT_COOKIES=[re.compile(p) for p in list_pattern] if list_pattern else []
        # Si hay una sesión base, copiar cookies filtradas
        def is_domain_allowed(domain: str) -> bool:
            return any(p.match(domain) for p in ACCEPT_COOKIES)
        if Session._base_session:
            for cookie in Session._base_session.cookies:
                if is_domain_allowed(cookie.domain):
                    self.cookies.set_cookie(cookie)
            # Copiar también headers si lo necesitas
            self.headers.update(Session._base_session.headers)

class Soup(BeautifulSoup):
    def __init__(
        self,
        html: Any,
        parser: str = "html.parser",
        unescape: bool = False,
        apply_css: bool = False,):
        super().__init__(html, parser)
        self.unescape = unescape
        self.apply_css = apply_css

class LazyUrl:
    def __init__(self, url:str, get_func:Callable[[str],str], obj,pp:Callable[[str],None]=None,alter:Callable[[str],None]=None):
        self.url = url  # Almacena la URL
        self.get = get_func  # Almacena la función get
        self.obj = obj  # Almacena la instancia de Vico
        self.pp = pp
        self.alter=alter

    def __call__(self):
        # Cuando se invoca el objeto, ejecuta la función get pasando la URL
        return self.get(self.url)

    def __str__(self):
        # Representación en cadena del objeto
        return f"LazyUrl({self.url})"

    def __repr__(self):
        # Representación más técnica (opcional, podría ser igual a __str__)
        return self.__str__()
    
_nfmaxi=2000
def get_max_range() -> int:
    return _nfmaxi
def _set_max_range(ran:int):
    global _nfmaxi
    _nfmaxi=ran
_nfresu=1080
def get_resolution() -> int:
    return _nfresu
def _set_resolution(ran:int):
    global _nfresu
    _nfresu=ran
def urljoin(a: AnyStr, b: AnyStr):
    """
    https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin
    """
    ...
def join(a:list[str]):
    if len(a)>2:
        return f'{a[0]}, Etc'
    return ','.join(a)

def query_url(url: str) -> dict[Any, str]:
    tags=url.split('?')[-1].split('&')
    dic={}
    for hh in tags:
        a,_,b=hh.partition('=')
        dic[a]=b.split('+')
    return dic

import time
from functools import wraps

class Nothing:
    pass

#Nothing = NothingType()

def try_n(
    n: int,
    sleep: Union[Callable[[int], float], float, None] = None,
    out: Any = Nothing
) -> Callable:
    """
    Decorator that retries the function `n` times if it raises an exception.

    :param n: Number of attempts.
    :param sleep: Time to wait between attempts (seconds), or a function that takes the attempt index and returns seconds.
    :param out: Default value to return if all attempts fail.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, n + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == n:
                        if out is not Nothing:
                            return out
                        else:
                            raise
                    if sleep:
                        wait = sleep(attempt) if callable(sleep) else sleep
                        time.sleep(wait)
        return wrapper
    return decorator

def clean_title(
    title: str,
    n: Optional[int] = None,
) -> str:
    #proh=['＼','／','：','＊','？','˝','〈〉','｜']
    traduccion = str.maketrans({
    '\\': '＼',
    '/': '／',
    ':': '：',
    '*': '＊',
    '?': '？',
    '"': '˝',
    '<': '〈',
    '>': '〉',
    '|': '｜',
    '\n': ' '
    })
    return title[:n].translate(traduccion)
def Invalid(
    self, s: str = "", e: Type[BaseException] = None, fail: bool = False
) -> None:
    """
    Notifies the user that an exception has occurred.
    """
    ...
def format_filename(title: str, id: Any, ext: str = ".", dirFormat=None):
    return f'{title} ({id})'

def get_ext(url: str) -> str:
    return '.'+url.partition('?')[0].split('.')[-1]
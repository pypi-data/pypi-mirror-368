from __future__ import annotations

import base64
import re
import warnings
from copy import deepcopy
from functools import cached_property
from typing import Annotated, Any, ClassVar, Literal, NamedTuple, Self, overload
from urllib.parse import parse_qsl, quote_plus, urlencode, urljoin

import courlan
import orjson
import tldextract
from loguru import logger
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, Url, core_schema

from good_common.pipeline import Attribute, Pipeline

from ._definitions import (
    ADULT_AND_VIDEOS,
    BIO_LINK_DOMAINS,
    DOMAIN_RULES,
    EXTENSION_REGEX,
    HTML_REDIRECT_DOMAINS,
    INDEX_PAGE_FILTER,
    NAVIGATION_FILTER,
    NOT_CRAWLABLE,
    REGEXP_GLOBAL_CANONICAL_PARAMS,
    REGEXP_SHORT_URL_EXCLUSIONS,
    REGEXP_TRACKING_PARAMS,
    REGEXP_TRACKING_VALUES,
    SHORT_URL_PROVIDERS,
)


def safe_username(username: str) -> str:
    try:
        return quote_plus(username)
    except Exception:
        logger.info(username)
        return ""


class UrlParseConfig(NamedTuple):
    remove_auth: bool = True
    remove_fragment: bool = True
    remove_standard_port: bool = True
    resolve_embedded_redirects: bool = False
    embedded_redirect_params = {"redirect", "redirect_to", "url"}
    canonical_params = {"id", "q", "v", "chash", "action"}
    force_https: bool = True
    short_url_exception_domains = {
        "fec.gov",
        "archive.is",
        "archive.org",
        "archive.today",
        "archive.ph",
    }


_default_config = UrlParseConfig()


type URLSerializableValue = str | int | float | bool


class Domain(str):
    def __new__(cls, domain: str | Domain, validate: bool = True):
        if isinstance(domain, Domain):
            return domain
        if not validate:
            _instance = super(Domain, cls).__new__(cls, domain)
            return _instance
        if not re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain):
            raise ValueError("Invalid domain name")

        _instance = super(Domain, cls).__new__(cls, domain)
        return _instance

    @property
    def tld(self):
        return self.rsplit(".", 1)[-1]

    @property
    def subdomains(self):
        return tuple(self.split(".")[:-2])

    @property
    def root(self):
        return self.split(".")[-2] + "." + self.tld

    @property
    def canonical(self):
        # www subdomain removed by all other subdomains kept
        subdomains = self.subdomains
        if subdomains and subdomains[0] == "www":
            subdomains = subdomains[1:]
        return ".".join(list(subdomains) + [self.root])

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


class URL(str):
    __match_args__ = (
        "scheme",
        "username",
        "password",
        "host",
        "host_no_www",
        "root_domain",
        "first_significant_subdomain",
        "port",
        "path",
        "path_parts",
        "query",
        "fragment",
        "clean",
        "canonical",
        "is_short_url",
        "is_html_redirect",
        "is_possible_short_url",
        "is_adult",
        "is_homepage",
        "is_bio_link_page",
        "is_not_crawlable",
        "is_navigation_page",
        "is_valid_url",
        "file_ext",
    )
    _strict: bool = False
    __clickhouse_type__: ClassVar[str] = "String"
    _url: Url

    @classmethod
    def build(
        cls,
        *,
        scheme: str,
        username: str | None = None,
        password: str | None = None,
        host: str,
        port: int | None = None,
        path: str | None = None,
        query: str
        | list[tuple[str, URLSerializableValue]]
        | dict[str, URLSerializableValue]
        | dict[str, tuple[URLSerializableValue]]
        | None = None,
        # flat_delimiter: str = ',',
        fragment: str | None = None,
    ) -> Self:
        _query = {}

        if isinstance(query, str) and len(query) > 0:
            _query = parse_qsl(query)

        elif isinstance(query, dict):
            # _query = {k: query[k] for k in sorted(query.keys())}
            _query = {k: query[k] for k in sorted(query.keys())}

        elif isinstance(query, list):
            _query = sorted(query, key=lambda x: x[0])

        _url = Url.build(
            scheme=scheme,
            username=safe_username(username) if username else None,
            password=password,
            host=host,
            port=port,
            path=path.lstrip("/") if path else None,
            query=urlencode(_query) if _query else None,
            fragment=fragment,
        )
        return cls(_url.unicode_string())

    def __new__(cls, url: str | URL, strict: bool = False):
        if isinstance(url, URL):
            return url
        _url = Url(url)
        instance = super().__new__(cls, _url.unicode_string())
        instance._url = _url
        instance._strict = strict
        return instance

    @classmethod
    def create(cls, *urls: str | URL, strict: bool = False) -> list[Self]:
        return [
            cls(url, strict=strict) if isinstance(url, str) else url for url in urls
        ]

    def __str__(self) -> str:
        return super().__str__()

    def join(self, *paths):
        _paths = ([self.path] if self.path else []) + list(paths)
        return URL.build(
            scheme=self.scheme,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path="/".join(_paths),
            query=self.query_params(format="flat"),
            fragment=self.fragment,
        )

    def update(
        self,
        *,
        scheme: str | None = None,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: int | None = None,
        path: str | None = None,
        query: dict[str, Any] | None = None,
        fragment: str | None = None,
        remove: set[str] | None = None,
    ):
        remove = remove or set()

        def _format_val(val):
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, float):
                return val
            elif isinstance(val, list):
                return ",".join(val)
            else:
                return orjson.dumps(val).decode()

        # format query-string
        if query is not None:
            query = {
                k: _format_val(v) for k, v in sorted(query.items(), key=lambda x: x[0])
            }
        else:
            query = self.query_params(format="dict")

        return URL.build(
            scheme=scheme or self.scheme if "scheme" not in remove else "https",
            username=username or self.username if "username" not in remove else None,
            password=password or self.password if "password" not in remove else None,
            host=host or self.host if "host" not in remove else None,
            port=port or self.port if "port" not in remove else None,
            path=path or self.path if "path" not in remove else None,
            query=query,
            fragment=fragment or self.fragment if "fragment" not in remove else None,
        )

    @classmethod
    def from_base_url(cls, base_url: str, url: str) -> URL:
        return URL(urljoin(base_url, url))

    @cached_property
    def scheme(self) -> str:
        return self._url.scheme

    @cached_property
    def username(self) -> str | None:
        return self._url.username

    @cached_property
    def password(self) -> str | None:
        return self._url.password

    @cached_property
    def host(self) -> Domain:
        if not self._url.host:
            if self._strict:
                raise ValueError("Host is not present in the URL")
            else:
                return ""
        return Domain(self._url.host)

    @cached_property
    def root_domain(self) -> Domain:
        return Domain(tldextract.extract(self.host).top_domain_under_public_suffix)

    @cached_property
    def host_root(self) -> Domain:
        if self.host.startswith("www."):
            return Domain(self.host[4:])
        return Domain(self.host)

    @cached_property
    def first_significant_subdomain(self) -> Domain | None:
        if self.root_domain == self.host_root:
            return None
        parts = [
            p for p in self.host_root[: -len(self.root_domain)].split(".") if p != ""
        ]
        return Domain(parts[-1])

    @cached_property
    def host_no_www(self) -> Domain:
        warnings.warn("host_no_www is deprecated, use host_root instead")
        return Domain(self.host_root)

    @cached_property
    def file_ext(self) -> str | None:
        if _match := EXTENSION_REGEX.search(self.path):
            return _match.group(0).strip("./")
        return None

    @cached_property
    def unicode_host(self) -> str | None:
        return self._url.unicode_host()

    @cached_property
    def port(self) -> int | None:
        return self._url.port

    @cached_property
    def path(self) -> str:
        return self._url.path or ""

    @cached_property
    def path_parts(self) -> tuple[str]:
        return tuple(self.path.strip("/").split("/") if self.path else [])

    @cached_property
    def query_string(self) -> str:
        return self._url.query or ""

    @cached_property
    def query(self) -> dict[str, URLSerializableValue]:
        return self.query_params(format="flat")

    @cached_property
    def fragment(self) -> str | None:
        return self._url.fragment

    @overload
    def query_params(
        self,
        format: Literal["plain"],
        flat_delimiter: str,
    ) -> list[tuple[str, URLSerializableValue]]: ...

    @overload
    def query_params(
        self,
        format: Literal["dict"],
        flat_delimiter: str,
    ) -> dict[str, tuple[URLSerializableValue]]: ...

    @overload
    def query_params(
        self,
        format: Literal["flat"],
        flat_delimiter: str = ",",
    ) -> dict[str, URLSerializableValue]: ...

    def query_params(
        self,
        format: Literal["plain", "dict", "flat"] = "flat",
        flat_delimiter: str = ",",
    ) -> (
        list[tuple[str, URLSerializableValue]]
        | dict[str, tuple[URLSerializableValue]]
        | dict[str, URLSerializableValue]
    ):
        _params = self._url.query_params()
        if format == "plain":
            return _params
        else:
            _output = {}
            for key, value in _params:
                if key not in _output:
                    _output[key] = []
                _output[key].append(value)

            if format == "dict":
                return {key: tuple(value) for key, value in _output.items()}
            else:
                return {
                    key: flat_delimiter.join(value) if len(value) > 1 else value[0]
                    for key, value in sorted(_output.items(), key=lambda x: x[0])
                }

        return _params

    def unicode_string(self) -> str:
        return self._url.unicode_string()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def clean_url(self, config: UrlParseConfig = UrlParseConfig()) -> URL:
        return _url_cleaning_pipeline.run_sync(url=self, config=config).url

    @cached_property
    def clean(self) -> URL:
        return self.clean_url()

    def canonicalize(
        self, config: UrlParseConfig = UrlParseConfig(resolve_embedded_redirects=True)
    ) -> URL:
        if self.scheme in ("http", "https"):
            _url = _url_canonicalization_pipeline.run_sync(
                url=self, config=config
            ).url.clean_url()

            if _url.scheme == "http":
                _url = URL.build(
                    scheme="https",
                    host=_url.host_root,
                    path=_url.path,
                    query=_url.query,
                )
            return _url
        return self

    @cached_property
    def canonical(self) -> URL:
        return self.canonicalize()

    @cached_property
    def is_short_url(self) -> bool:
        return any(
            provider == self.host
            for provider in SHORT_URL_PROVIDERS
            | HTML_REDIRECT_DOMAINS
            | BIO_LINK_DOMAINS
        )

    @cached_property
    def is_html_redirect(self) -> bool:
        return self.host in HTML_REDIRECT_DOMAINS

    @cached_property
    def is_possible_short_url(self) -> bool:
        if self.path is None:
            return False
        if self.is_short_url:
            return True
        return all(
            [
                (
                    (len(self.host.replace(".", "")) < 10)
                    or (self.host.endswith(".link"))
                    or (self.host.startswith("on."))
                    or (self.host.startswith("go."))
                    or (self.host.startswith("l."))
                ),
                self.host not in _default_config.short_url_exception_domains,
                len(self.path.strip("/")) < 10,
                self.path.count("/") == 1,
            ]
        ) and not REGEXP_SHORT_URL_EXCLUSIONS.match(self.host)

    @cached_property
    def is_adult(self) -> bool:
        return bool(ADULT_AND_VIDEOS.search(self))

    @cached_property
    def is_homepage(self) -> bool:
        return bool(INDEX_PAGE_FILTER.match(self.path)) or self.path == "/"

    @cached_property
    def is_not_crawlable(self) -> bool:
        return bool(NOT_CRAWLABLE.search(self))

    @cached_property
    def is_navigation_page(self) -> bool:
        return bool(NAVIGATION_FILTER.search(self))

    @cached_property
    def is_valid_url(self) -> bool:
        return courlan.filters.is_valid_url(self)

    @cached_property
    def is_bio_link_page(self):
        return self.host_root in BIO_LINK_DOMAINS

    def lang_filter(
        self,
        language: str | None = None,
        strict: bool = False,
        trailing_slash: bool = True,
    ) -> bool:
        return courlan.filters.lang_filter(
            self, language=language, strict=strict, trailing_slash=trailing_slash
        )

    def type_filter(
        self,
        strict: bool = False,
        with_nav: bool = False,
    ) -> bool:
        return courlan.filters.type_filter(self, strict=strict, with_nav=with_nav)

    def search(
        self,
        pat: str,
        flags: int = 0,
    ):
        return re.search(pat, self, flags)

    def match(
        self,
        pat: str,
        flags: int = 0,
    ):
        return re.match(pat, self, flags)

    def __div__(self, other):
        return self.join(other)


def _basic_clean(url: URL, config: UrlParseConfig) -> Annotated[URL, Attribute("url")]:
    _query = url.query_params(format="plain")
    return URL.build(
        scheme=url.scheme.lower() if not config.force_https else "https",
        username=url.username if not config.remove_auth else None,
        password=url.password if not config.remove_auth else None,
        host=url.host.lower(),
        port=url.port
        if url.port != 80 and url.port != 443 and not config.remove_standard_port
        else None,
        path=url.path,
        query=_query,
        fragment=url.fragment if not config.remove_fragment else None,
    )


def _domain_specific_url_rewrites(
    url: URL, config: UrlParseConfig
) -> Annotated[URL, Attribute("url")]:
    """
    Some domains have predictable URL redirect structures that do not require resolving the URL.
    """
    match url:
        case URL(host="youtu.be", path=path) if path is not None:
            return URL.build(
                scheme="https",
                host="www.youtube.com",
                path="/watch",
                query=[("v", path[1:])],
            )

        case URL(host="discord.gg", path=path) if path is not None:
            return URL.build(
                scheme="https",
                host="discord.com",
                path="/invite/" + path[1:],
            )

        case URL(host="twitter.com", path=path) if path is not None:
            return URL.build(
                scheme="https",
                host="x.com",
                path=path[1:],
                query=url.query_params(format="plain"),
            )

    return url


def _resolve_embedded_redirects(url: URL, config: UrlParseConfig) -> URL:
    """
    Resolve embedded redirects in URLs.
    """
    query = url.query_params(format="flattened")
    no_www_domain = url.host.lstrip("www.")

    keys_of_interest = set()
    if config.resolve_embedded_redirects:
        keys_of_interest = config.embedded_redirect_params

    match (no_www_domain, query):
        case ("facebook.com", {"u": [u]}):
            return URL(u)

        case ("google.com", {"url": [u]}):
            return URL(u)

        case (str() as host, dict() as target_dict):
            for key, value in target_dict.items():
                if key in keys_of_interest:
                    if isinstance(value, str):
                        value = tuple([value])
                    for v in value:
                        if v.startswith("http"):
                            return URL(v)
                        elif v.startswith("//"):
                            return URL.build(
                                scheme=url.scheme,
                                host=host,
                                path=v[2:],
                            )
                        elif "/" not in value and isinstance(value, str):
                            try:
                                return URL(base64.urlsafe_b64decode(value).decode())
                            except Exception:
                                pass
                    # if value.startswith("http"):
                    #     return URL(value)
                    # elif value.startswith("//"):
                    #     return URL.build(
                    #         scheme=url.scheme,
                    #         host=host,
                    #         path=value[2:],
                    #     )
                    # elif "/" not in value and isinstance(value, str):
                    #     try:
                    #         return URL(base64.urlsafe_b64decode(value).decode())
                    #     except Exception:
                    #         pass
                    # else:
                    #     return URL.build(
                    #         scheme=url.scheme,
                    #         host=host,
                    #         path=value,
                    #     )

                    # return URL(value)

    return url


def _filter_canonical_params(url: URL, config: UrlParseConfig) -> URL:
    non_canonical_params = set()

    _config = deepcopy(config)

    _host = url.host

    domain_rules = DOMAIN_RULES[_host] or {}

    if domain_rules.get("disable"):
        logger.warning(f"Canonicalization disabled for domain {_host}")
        return url
    if domain_rules.get("canonical"):
        _config.canonical_params.update(domain_rules["canonical"])
    if domain_rules.get("non_canonical"):
        non_canonical_params.update(domain_rules["non_canonical"])
    if domain_rules.get("force_www") and not _host.startswith("www."):
        _host = f"www.{_host}"

    new_query_params = []

    for key, value in url.query_params(format="plain"):
        if key in _config.canonical_params:
            new_query_params.append((key, value))

        elif REGEXP_GLOBAL_CANONICAL_PARAMS.match(key) or (
            key not in non_canonical_params
            and not REGEXP_TRACKING_PARAMS.match(key)
            and not REGEXP_TRACKING_VALUES.match(value)
        ):
            new_query_params.append((key, value))
        else:
            pass

    return URL.build(
        scheme=url.scheme,
        username=url.username,
        password=url.password,
        host=_host,
        port=url.port,
        path=url.path,
        query=new_query_params,
        fragment="",
    )


_url_cleaning_pipeline = Pipeline(_basic_clean, _domain_specific_url_rewrites)

_url_canonicalization_pipeline = Pipeline(
    _basic_clean,
    _domain_specific_url_rewrites,
    _resolve_embedded_redirects,
    _filter_canonical_params,
)


def to_url(url: str | URL) -> URL:
    if isinstance(url, URL):
        return url
    return URL(url)


__all__ = ["URL", "to_url", "Domain"]

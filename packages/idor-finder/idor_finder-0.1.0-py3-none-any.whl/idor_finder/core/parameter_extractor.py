import json
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup


UUID_REGEX = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


@dataclass
class ExtractedParam:
    name: str
    value: Optional[str]
    source: str  # query|form|json|cookie|header|path|discovered


class ParameterExtractor:
    def extract_from_url(self, url: str) -> List[ExtractedParam]:
        params: List[ExtractedParam] = []
        if "?" in url:
            query = url.split("?", 1)[1]
            for pair in query.split("&"):
                if not pair:
                    continue
                if "=" in pair:
                    name, value = pair.split("=", 1)
                else:
                    name, value = pair, None
                if name:
                    params.append(ExtractedParam(name=name, value=value, source="query"))
        # path params that look like UUIDs or numeric IDs
        for match in UUID_REGEX.finditer(url):
            params.append(ExtractedParam(name="uuid_path", value=match.group(0), source="path"))
        for match in re.finditer(r"/(\d{2,})", url):
            params.append(ExtractedParam(name="id_path", value=match.group(1), source="path"))
        return params

    def extract_from_html(self, html: str) -> List[ExtractedParam]:
        params: List[ExtractedParam] = []
        soup = BeautifulSoup(html, "html.parser")
        for form in soup.find_all("form"):
            for inp in form.find_all(["input", "select", "textarea"]):
                name = inp.get("name") or inp.get("id")
                if not name:
                    continue
                value = inp.get("value")
                params.append(ExtractedParam(name=name, value=value, source="form"))
        # hidden inputs
        for inp in soup.find_all("input", {"type": "hidden"}):
            name = inp.get("name") or inp.get("id")
            if name:
                params.append(ExtractedParam(name=name, value=inp.get("value"), source="form"))
        return params

    def extract_from_json(self, body: str) -> List[ExtractedParam]:
        params: List[ExtractedParam] = []
        try:
            data = json.loads(body)
        except Exception:
            return params

        def walk(obj: object, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, (dict, list)):
                        walk(v, key)
                    else:
                        params.append(ExtractedParam(name=key, value=str(v), source="json"))
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    key = f"{prefix}[{idx}]" if prefix else f"[{idx}]"
                    if isinstance(item, (dict, list)):
                        walk(item, key)
                    else:
                        params.append(ExtractedParam(name=key, value=str(item), source="json"))

        walk(data)
        return params

    def extract_from_headers(self, headers: Dict[str, str]) -> List[ExtractedParam]:
        params: List[ExtractedParam] = []
        for k, v in headers.items():
            params.append(ExtractedParam(name=k, value=v, source="header"))
        return params

    def extract_from_cookies(self, cookies: Dict[str, str]) -> List[ExtractedParam]:
        params: List[ExtractedParam] = []
        for k, v in cookies.items():
            params.append(ExtractedParam(name=k, value=v, source="cookie"))
        return params

    @staticmethod
    def normalize_param_names(names: Iterable[str]) -> List[str]:
        normalized: List[str] = []
        seen = set()
        for name in names:
            variants = set(
                [
                    name,
                    name.lower(),
                    name.upper(),
                    name.title(),
                    name.replace("_", ""),
                    name.replace("-", ""),
                    name.replace("_", "-")
                    .replace("-", "_")
                    .strip("-_"),
                ]
            )
            for v in variants:
                if v and v not in seen:
                    seen.add(v)
                    normalized.append(v)
        return normalized



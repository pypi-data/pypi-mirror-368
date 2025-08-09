import json
from urllib.request import urlopen


class _PyPiMetadata:
    url = "https://pypi.org/pypi/changelogbump/json"

    @classmethod
    def get(cls) -> dict:
        with urlopen(cls.url) as response:
            return json.loads(response.read().decode())

    @classmethod
    def version(cls) -> str:
        _meta: dict = cls.get()
        return _meta["info"]["version"]

from pydantic import BaseModel
from functools import lru_cache


class DepagConfig(BaseModel):
    wsdl_url: str
    username: str | None = None
    password: str | None = None


@lru_cache
def get_config() -> DepagConfig:
    return DepagConfig(
        wsdl_url="https://pagopa.comune.sanlazzaro.bo.it/PagamentiOnLine/services/depag?wsdl",
        username=None,
        password=None,
    )

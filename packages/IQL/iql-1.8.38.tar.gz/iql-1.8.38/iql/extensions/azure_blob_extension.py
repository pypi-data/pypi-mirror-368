import logging
from dataclasses import dataclass
from html import unescape
from io import BytesIO

import pandas as pd
from azure.core.credentials import AccessToken, TokenCredential
from azure.storage.blob import BlobServiceClient

from iql import IqlExtension, SubQuery, iql_cache, register_extension

_CREDENTIAL = None

logger = logging.getLogger(__name__)


class StaticTokenCredential(TokenCredential):
    def __init__(self, access_token: AccessToken):
        self._access_token = access_token

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        return self._access_token


@dataclass
class AzureBlobExtension(IqlExtension):
    """
    DuckDB does support native reading of certain file types.
    This is fine for XLSX files, but some file types need different engines, such as "xls", that duckdb doesn't support
    """

    param_replace_text = False
    keyword: str
    is_async: bool = False

    @iql_cache
    def executeimpl(self, sq: SubQuery) -> pd.DataFrame:
        blob_url: str = sq.options["url"]  # type: ignore

        logger.info("Reading %s", blob_url)
        engine: str | None = sq.options.get("engine", None)  # type: ignore
        account_url = blob_url.split("/")[2]
        # account_name = blob_url.split(".")[0]
        filename = unescape(blob_url.split("/")[-1])
        container = blob_url.split("/")[3]

        coerce_str = sq.options.get(
            "coerce_str", True
        )  # by default, cooerce everything to string. Avoids parquet export errors.

        if not filename.endswith(".xls") and not filename.endswith(".xlsx"):
            raise ValueError("Only .xls or .xlsx is supported")

        if filename.endswith(".xls") and engine is None:
            engine = "calamine"

        blob_service_client = BlobServiceClient(account_url, credential=_CREDENTIAL)
        blob_client = blob_service_client.get_blob_client(container=container, blob=filename)

        data = blob_client.download_blob().readall()
        data_io = BytesIO(data)

        # The astype(str) is needed because of the mixed data types in the columns, which will break parquet export
        if engine is not None:
            result_df = pd.read_excel(data_io, engine=engine)  # type: ignore
        else:
            result_df = pd.read_excel(data_io)

        if coerce_str:
            result_df = result_df.astype(str)

        result_df["blob_url"] = blob_url
        return result_df


def register(keyword: str):
    extension = AzureBlobExtension(keyword=keyword, subword="excel")
    # extension.cache = cache.MemoryAndFileCache(max_age=3600 * 24, return_pyarrow_table=False)
    register_extension(extension)

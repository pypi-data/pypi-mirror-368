import logging
from abc import abstractmethod
from typing import Dict, Iterable, Optional

from .result import IqlResult

logger = logging.getLogger(__name__)


class IqlDatabase:
    @abstractmethod
    def execute_query(
        self,
        query: str,
        context: Optional[Dict[str, object]],
        completed_results: Iterable[IqlResult],
        raw: bool = False,
        parameters: Optional[Iterable] = None,
    ) -> Optional[IqlResult]:
        pass

    @abstractmethod
    def get_connection(self) -> object:
        pass

    @abstractmethod
    def close_db(self):
        pass


class IqlDatabaseConnector:
    @abstractmethod
    def create_database(self) -> IqlDatabase:
        pass

    @abstractmethod
    def create_database_from_con(self, con: object) -> IqlDatabase:
        pass

from datetime import date

from quantification.core import (
    Field,
    Stock,
    DataPanel,
    BaseCombinedAPI
)


class DataAPI(BaseCombinedAPI):
    def query(
            self,
            *,
            start_date: date,
            end_date: date,
            fields: list[Field],
            stock: type[Stock] = None,
            index: str = None,
            keywords: list[str] = None
    ) -> DataPanel:
        ...

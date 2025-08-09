import sys
from pathlib import Path
from typing import TYPE_CHECKING

import clr  # type: ignore[import-untyped]

SOURCE_FOLDER = (Path(__file__).parent / "libs").absolute().as_posix()
sys.path.insert(0, SOURCE_FOLDER)
clr.AddReference("Translation")  # type: ignore
# When type checking, we import from the stub file. When running, we import from the actual C# module.
if TYPE_CHECKING:
    from .Translation import (  # type: ignore[import-untyped]
        DataViewQueryTranslationResult,
        PrototypeQuery,
    )
else:
    from Translation import DataViewQueryTranslationResult, PrototypeQuery


class TranslationResult:
    """Result of the query translation, converted to Python structures."""

    dax: str
    """The translated DAX expression for the given SSAS instance."""

    column_mapping: dict[str, str]
    """Mapping from the names of the columns in the SELECT statement to the DAX column names.
    
    Example:
    
        ```json
        {'Sum(Sales.Sales Amount)': '[SumSales_Amount]', 'Sales.Sales Amount by Due Date': '[Sales_Amount_by_Due_Date]', 'Date.Fiscal.Month': 'Date[Month]'}
        ```
    """

    def __init__(self, data: DataViewQueryTranslationResult):
        self.data = data
        self.dax = data.DaxExpression
        self.column_mapping = dict(
            zip(
                data.SelectNameToDaxColumnName.Keys,
                data.SelectNameToDaxColumnName.Values,
            )
        )


def prototype_query(query: str, db_name: str, port: int) -> TranslationResult:
    """Main entrypoint for this library."""
    ret = PrototypeQuery.Translate(query, db_name, port, SOURCE_FOLDER)
    return TranslationResult(ret)

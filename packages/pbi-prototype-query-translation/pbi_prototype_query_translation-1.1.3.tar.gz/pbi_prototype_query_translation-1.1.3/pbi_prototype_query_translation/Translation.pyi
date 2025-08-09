class CSharpDict:
    """The standard C# dictionary type."""

    Keys: list[str]
    """The keys of the dictionary as a list."""

    Values: list[str]
    """The values of the dictionary as a list."""

class DataViewQueryTranslationResult:
    """Result of the query translation."""

    DaxExpression: str
    """The translated DAX expression for the given SSAS instance."""

    SelectNameToDaxColumnName: CSharpDict
    """Mapping from the names of the columns in the SELECT statement to the DAX column names.
    
    Example:
    
        ```json
        {'Sum(Sales.Sales Amount)': '[SumSales_Amount]', 'Sales.Sales Amount by Due Date': '[Sales_Amount_by_Due_Date]', 'Date.Fiscal.Month': 'Date[Month]'}
        ```
    """

class PrototypeQuery:
    """Object representing a query prototype on the C# side."""

    @staticmethod
    def Translate(
        query: str, dbName: str, port: int, workingDirectory: str | None = None
    ) -> DataViewQueryTranslationResult: ...
    """Translates a query to DAX expression."""

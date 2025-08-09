class CSharpDict:
    Keys: list[str]
    Values: list[str]


class DataViewQueryTranslationResult:
    DaxExpression: str
    SelectNameToDaxColumnName: CSharpDict


def prototype_query(query: str, db_name: str, port: int) -> "DataViewQueryTranslationResult":
    ...
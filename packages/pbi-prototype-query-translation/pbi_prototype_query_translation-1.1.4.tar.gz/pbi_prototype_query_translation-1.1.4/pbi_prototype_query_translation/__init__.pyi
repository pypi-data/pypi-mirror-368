class CSharpDict:
    Keys: list[str]
    Values: list[str]

class DataViewQueryTranslationResult:
    DaxExpression: str
    SelectNameToDaxColumnName: CSharpDict

class TranslationResult:
    dax: str
    column_mapping: dict[str, str]

def prototype_query(query: str, db_name: str, port: int) -> "TranslationResult": ...

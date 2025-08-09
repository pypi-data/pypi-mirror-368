# Overview

This is a single use library to translate the Prototype Query objects found in the Layout json to DAX that can be run against a SSAS instance. It requires a running SSAS instance.


# Example
??? note "Input Prototype Query"

    In this example, you can see the 5 attributes (+ the version) that roughly correspond to their name equivalents in SQL. Currently, it's ambiguous what the `Transform` section is used for. 

    Note that only the `From` section references the table names directly: the other sections use the From entity name, generally the first letter of the table name as a reference.

    ```json
    {
        "Version": 2,
        "From": [
            {
                "Entity": "Date",
                "Name": "d",
                "Type": 0
            },
            {
                "Entity": "Sales",
                "Name": "s",
                "Type": 0
            }
        ],
        "Select": [
            {
                "Aggregation": {
                    "Expression": {
                        "Column": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "s"
                                }
                            },
                            "Property": "Sales Amount"
                        }
                    },
                    "Function": 0
                },
                "Name": "Sum(Sales.Sales Amount)"
            },
            {
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "Source": "s"
                        }
                    },
                    "Property": "Sales Amount by Due Date"
                },
                "Name": "Sales.Sales Amount by Due Date"
            },
            {
                "HierarchyLevel": {
                    "Expression": {
                        "Hierarchy": {
                            "Expression": {
                                "SourceRef": {
                                    "Source": "d"
                                }
                            },
                            "Hierarchy": "Fiscal"
                        }
                    },
                    "Level": "Month"
                },
                "Name": "Date.Fiscal.Month"
            }
        ],
        "Where": [
            {
                "Condition": {
                    "In": {
                        "Expressions": [
                            {
                                "Column": {
                                    "Expression": {
                                        "SourceRef": {
                                            "Source": "d"
                                        }
                                    },
                                    "Property": "Fiscal Year"
                                }
                            }
                        ],
                        "Values": [
                            [
                                {
                                    "Literal": {
                                        "Value":"'FY2019'"
                                    }
                                }
                            ]
                        ]
                    }
                }
            }
        ],
        "OrderBy": [],
        "Transform":[]
    }

    ```json
    {
    "Version": 2,
    "From": [
        {
        "Entity": "Date",
        "Name": "d",
        "Type": 0
        },
        {
        "Entity": "Sales",
        "Name": "s",
        "Type": 0
        }
    ],
    "Select": [
        {
        "Aggregation": {
            "Expression": {
            "Column": {
                "Expression": {
                "SourceRef": {
                    "Source": "s"
                }
                },
                "Property": "Sales Amount"
            }
            },
            "Function": 0
        },
        "Name": "Sum(Sales.Sales Amount)"
        },
        {
        "Measure": {
            "Expression": {
            "SourceRef": {
                "Source": "s"
            }
            },
            "Property": "Sales Amount by Due Date"
        },
        "Name": "Sales.Sales Amount by Due Date"
        },
        {
        "HierarchyLevel": {
            "Expression": {
            "Hierarchy": {
                "Expression": {
                "SourceRef": {
                    "Source": "d"
                }
                },
                "Hierarchy": "Fiscal"
            }
            },
            "Level": "Month"
        },
        "Name": "Date.Fiscal.Month"
        }
    ],
    "Where": [
        {
        "Condition": {
            "In": {
            "Expressions": [
                {
                "Column": {
                    "Expression": {
                    "SourceRef": {
                        "Source": "d"
                    }
                    },
                    "Property": "Fiscal Year"
                }
                }
            ],
            "Values": [
                [
                {
                    "Literal": {
                    "Value": "'FY2019'"
                    }
                }
                ]
            ]
            }
        }
        }
    ],
    "OrderBy": [],
    "Transform": []
    }
    ```

??? note "DAX Result"

    ```dax
    DEFINE
            VAR __DS0FilterTable =
                    TREATAS({"FY2019"}, 'Date'[Fiscal Year])

            VAR __DS0Core =
                    SUMMARIZECOLUMNS(
                            'Date'[Month],
                            __DS0FilterTable,
                            "SumSales_Amount", CALCULATE(SUM('Sales'[Sales Amount])),
                            "Sales_Amount_by_Due_Date", 'Sales'[Sales Amount by Due Date]
                    )

    EVALUATE
            __DS0Core
    ```

??? note "Column Mapping Result"

    The column mapping is a dictionary that maps the names of the columns in the SELECT statement to the DAX column names. This is necessary to map the DAX results back to the original query structure.

    ```json
    {
        "Sum(Sales.Sales Amount)": "[SumSales_Amount]",
        "Sales.Sales Amount by Due Date": "[Sales_Amount_by_Due_Date]",
        "Date.Fiscal.Month": "Date[Month]"
    }
    ```
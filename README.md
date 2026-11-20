# Fabric AdventureWorks Lakehouse

Build a Microsoft Fabric Lakehouse on the AdventureWorksDW sample data: 24 clean files, one notebook that loads them into typed Delta tables, and a set of SQL views that keep the dates current so your demos always end today. BEST DAY EVER!!!

## What is in the repo

| Folder | Contents |
| --- | --- |
| `AdventureWorks/` | 16 dimension and 8 fact tables as delimited text files |
| `NoteBooks/LoadAdventureWorks.ipynb` | Loads every file into a Delta table with an explicit schema, then validates row counts, keys and relationships |
| `Views/` | T-SQL views for the Lakehouse SQL analytics endpoint that shift all dates forward to today |
| `PowerQueryGen1Templates/` | Dataflow Gen1 template that reads the same tables from a local `AdventureWorksDW2019` SQL Server database (an alternative to the files) |

## Quick start

1. Create a Lakehouse in a Fabric workspace.
2. Upload the `AdventureWorks` folder to the Lakehouse **Files** area, so the files sit at `Files/AdventureWorks/*.csv`.
3. Import `NoteBooks/LoadAdventureWorks.ipynb`, attach the Lakehouse as the default Lakehouse, and run all cells. The last cell fails with a list of problems if anything did not load correctly.
4. Open the SQL analytics endpoint of the Lakehouse and run the scripts in `Views/`. Run `vwFactResellerSales` before `vwRptEmployeeResellerSales`; the rest can run in any order.

If your Lakehouse has schemas enabled, set `TARGET = "Tables/dbo"` in the first code cell of the notebook.

## File format

Every file in `AdventureWorks/` uses the same format:

| Setting | Value |
| --- | --- |
| Delimiter | pipe (`\|`) |
| Encoding | UTF-8, no byte order mark |
| Line endings | LF |
| Header | first row, column names match AdventureWorksDW |
| Quoting | none; a `"` in a value is literal text |
| Nulls | empty field |
| Dates | `yyyy-MM-dd` |
| Booleans | `true` / `false` |
| Numbers | plain decimals with a leading zero, no scientific notation |

Reading a file outside the notebook:

- **Spark:** `sep="|"`, `quote=""`, `header=true`
- **Power Query:** `Csv.Document(file, [Delimiter = "|", Encoding = 65001, QuoteStyle = QuoteStyle.None])`

## Tables

| Table | Rows | Key |
| --- | ---: | --- |
| DimAccount | 99 | AccountKey |
| DimCurrency | 105 | CurrencyKey |
| DimCustomer | 18,484 | CustomerKey |
| DimDate | 3,652 | DateKey |
| DimDepartmentGroup | 7 | DepartmentGroupKey |
| DimEmployee | 296 | EmployeeKey |
| DimGeography | 655 | GeographyKey |
| DimOrganization | 14 | OrganizationKey |
| DimProduct | 606 | ProductKey |
| DimProductCategory | 4 | ProductCategoryKey |
| DimProductSubcategory | 37 | ProductSubcategoryKey |
| DimPromotion | 16 | PromotionKey |
| DimReseller | 701 | ResellerKey |
| DimSalesReason | 10 | SalesReasonKey |
| DimSalesTerritory | 11 | SalesTerritoryKey |
| DimScenario | 3 | ScenarioKey |
| FactCallCenter | 120 | FactCallCenterID |
| FactCurrencyRate | 14,264 | CurrencyKey, DateKey |
| FactFinance | 39,409 | FinanceKey |
| FactInternetSales | 60,398 | SalesOrderNumber, SalesOrderLineNumber |
| FactProductInventory | 776,286 | ProductKey, DateKey |
| FactResellerSales | 60,855 | SalesOrderNumber, SalesOrderLineNumber |
| FactSalesQuota | 163 | SalesQuotaKey |
| FactSurveyResponse | 2,727 | SurveyResponseKey |

Differences from the Microsoft original, all on purpose: the Spanish and French columns, the other translated product descriptions, and the image columns (`LargePhoto`, `EmployeePhoto`, `SalesTerritoryImage`) are left out. Every remaining value matches the original, except a handful of names and addresses in `DimEmployee` and `DimReseller` where accented characters are garbled in the original and are correct here (for example `Königsteiner Straße`).

## The views

The source data runs from late 2010 to 2014. Each fact view moves its dates forward by a whole number of days so that the most recent data lands on today, and recalculates the date keys to match. `vwDimDate` moves the calendar the same way and ends on December 31, so date keys from every fact view have a matching row. Because the shift uses `GETDATE()`, the data rolls forward every day without a reload.

Use the views, not the base tables, in a semantic model when you want current dates.

## Credits

The data is Microsoft's [AdventureWorksDW sample](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/data-warehouse-install-script). Thanks to MIM for help with the original load code.

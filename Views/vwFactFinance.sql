CREATE VIEW [dbo].[vwFactFinance] as


SELECT [FinanceKey]
      ,CAST(CONVERT(VARCHAR(10), DATEADD(d, DATEOFFSET, [Date]), 112) as INT) [DateKey]
      ,[OrganizationKey]
      ,[DepartmentGroupKey]
      ,[ScenarioKey]
      ,[AccountKey]
      ,[Amount]
	  ,DATEADD(d, DATEOFFSET, [Date]) [Date]

  FROM [silver].[FactFinance] 
  
    JOIN (  SELECT Datediff(d, [FullDateAlternateKey], getdate()) DATEOFFSET
				 FROM [silver].[DimDate] DD 
			  Inner Join (
				  SELECT MAX([DateKey]) DK
				  FROM [silver].[FactFinance] FPI ) Offset ON
				  DD.DateKey = Offset.DK)OFFSET ON 1=1

GO
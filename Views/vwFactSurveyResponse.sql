CREATE VIEW [dbo].[vwFactSurveyResponse] as


SELECT [SurveyResponseKey]
      ,CAST(CONVERT(VARCHAR(10), DATEADD(d, DATEOFFSET, [Date]), 112) as INT) [DateKey]
      ,[CustomerKey]
      ,[ProductCategoryKey]
      ,[EnglishProductCategoryName]
      ,[ProductSubcategoryKey]
      ,[EnglishProductSubcategoryName]
	  ,DATEADD(d, DATEOFFSET, [Date]) [Date]
  
  FROM [silver].[FactSurveyResponse] 

      JOIN (  SELECT Datediff(d, [FullDateAlternateKey], getdate()) DATEOFFSET
				 FROM [silver].[DimDate] DD 
			  Inner Join (
				  SELECT MAX([DateKey]) DK
				  FROM [silver].[FactSurveyResponse] FPI ) Offset ON
				  DD.DateKey = Offset.DK)OFFSET ON 1=1



GO
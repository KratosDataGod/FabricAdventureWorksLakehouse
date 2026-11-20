CREATE VIEW [dbo].[vwFactCurrencyRate] as

SELECT [CurrencyKey]
	  ,CAST(CONVERT(VARCHAR(10), DATEADD(d, DATEOFFSET, [Date]), 112) as INT) [DateKey]
      ,[AverageRate]
      ,[EndOfDayRate]
	  ,DATEADD(d, DATEOFFSET, [Date]) [Date]
  
  FROM [silver].[FactCurrencyRate] 

    JOIN (  SELECT Datediff(d, [FullDateAlternateKey], getdate()) DATEOFFSET
				 FROM [silver].[DimDate] DD 
			  Inner Join (
				  SELECT MAX([DateKey]) DK
				  FROM [silver].[FactCurrencyRate] FPI ) Offset ON
				  DD.DateKey = Offset.DK)OFFSET ON 1=1




GO
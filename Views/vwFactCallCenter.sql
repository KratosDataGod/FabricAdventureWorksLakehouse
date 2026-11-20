
CREATE VIEW [dbo].[vwFactCallCenter] as


SELECT [FactCallCenterID]
	  ,CAST(CONVERT(VARCHAR(10), DATEADD(d, DATEOFFSET, [Date]), 112) as INT) [DateKey]
      ,[WageType]
      ,[Shift]
      ,[LevelOneOperators]
      ,[LevelTwoOperators]
      ,[TotalOperators]
      ,[Calls]
      ,[AutomaticResponses]
      ,[Orders]
      ,[IssuesRaised]
      ,[AverageTimePerIssue]
      ,[ServiceGrade]
	  ,DATEADD(d, DATEOFFSET, [Date]) [Date]

  FROM [silver].[FactCallCenter] 

  JOIN (  SELECT Datediff(d, [FullDateAlternateKey], getdate()) DATEOFFSET
				 FROM [silver].[DimDate] DD 
			  Inner Join (
				  SELECT MAX([DateKey]) DK
				  FROM [silver].[FactCallCenter] FPI ) Offset ON
				  DD.DateKey = Offset.DK)OFFSET ON 1=1

GO


CREATE VIEW [dbo].[vwRptEmployeeResellerSales]
AS
SELECT FRS.[ProductKey]
      ,DPS.ProductSubcategoryKey
	  ,DPC.ProductCategoryKey
      ,[OrderDateKey]
      ,[DueDateKey]
      ,[ShipDateKey]
      ,FRS.[ResellerKey]
      ,FRS.[EmployeeKey]
      ,FRS.[PromotionKey]
      ,[CurrencyKey]
      ,FRS.[SalesTerritoryKey]
	  ,DE.FirstName + ' ' + [LastName] as EmployeeName
	  ,[Title]
	  ,[HireDate]
	  ,[LoginID]
	  ,[EmailAddress]
	  ,DE.[Phone] as EmployeePhone
	  ,[ResellerName]
	  ,DR.[Phone] as ResellerPhone
	  ,[BusinessType]
	  ,[YearOpened]
	  ,[FirstOrderYear]
	  ,[AnnualSales]
	  ,[AnnualRevenue]
	  ,DR.[ProductLine]
	  ,DR.[AddressLine1]
	  ,DR.AddressLine2
	  ,DST.SalesTerritoryRegion
	  ,DST.SalesTerritoryGroup
	  ,DST.SalesTerritoryCountry
	  ,DPC.EnglishProductCategoryName as ProductCategory
	  ,DPS.EnglishProductSubcategoryName as ProductSubCategory
	  ,DP.EnglishProductName as ProductName
	  ,DP.EnglishDescription as ProductDescription
	  ,DPR.EnglishPromotionName as PromotionName
	  ,DPR.EnglishPromotionCategory as PromotionCategory
	  ,DPR.EnglishPromotionType as PromotionType
	  ,DPR.MaxQty as PromotionMaxQty
	  ,DPR.DiscountPct as PromotionDiscountPct
      ,[SalesOrderNumber]
      ,[SalesOrderLineNumber]
      ,[RevisionNumber]
      ,[OrderQuantity]
      ,[UnitPrice]
      ,[ExtendedAmount]
      ,[UnitPriceDiscountPct]
      ,[DiscountAmount]
      ,[ProductStandardCost]
      ,[TotalProductCost]
      ,[SalesAmount]
      ,[TaxAmt]
      ,[Freight]
      ,[CarrierTrackingNumber]
      ,[CustomerPONumber]
      ,[OrderDate]
      ,[DueDate]
      ,[ShipDate]
	  --SELECT COUNT(*) CNT
  FROM [dbo].[vwFactResellerSales] FRS 

  INNER JOIN [silver].[DimEmployee] DE 
	ON FRS.EmployeeKey = DE.EmployeeKey

  INNER JOIN [silver].[DimProduct] DP  
	ON FRS.ProductKey = DP.ProductKey

  INNER JOIN [silver].[DimProductSubcategory] DPS
	ON DP.ProductSubcategoryKey = DPS.ProductSubcategoryKey

  INNER JOIN [silver].[DimProductCategory] DPC 
	ON DPS.ProductCategoryKey = DPC.ProductCategoryKey

  INNER JOIN [silver].[DimReseller] DR 
	ON FRS.ResellerKey = DR.ResellerKey

  INNER JOIN [silver].[DimPromotion] DPR 
	ON FRS.PromotionKey = DPR.PromotionKey

  INNER JOIN [silver].[DimSalesTerritory] DST 
	ON FRS.SalesTerritoryKey = DST.SalesTerritoryKey


GO



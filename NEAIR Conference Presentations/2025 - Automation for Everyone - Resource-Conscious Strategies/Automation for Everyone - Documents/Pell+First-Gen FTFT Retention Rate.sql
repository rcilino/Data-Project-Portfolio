With FG_CTE AS
(SELECT *

FROM
	(
	SELECT b.[ISIR_FAFSA_ID]
		  ,b.IFAF_STUDENT_ID
		  ,b.IFAF_IMPORT_YEAR
		  ,b.IFAF_STUDENT_ID+'*'+b.IFAF_IMPORT_YEAR as FG_CTE_IDX
		  ,b.ISIR_RECEIPT_DATE
		  ,ROW_NUMBER() OVER(PARTITION BY IFAF_STUDENT_ID, IFAF_IMPORT_YEAR ORDER BY b.ISIR_FAFSA_ID desc) as rn
		  ,[IFAF_FATHER_GRADE_LVL]
		  ,[IFAF_MOTHER_GRADE_LVL]
		  ,[IRES_SPECIAL_CIRCUM_FLAG]
		  ,case when [IFAF_FATHER_GRADE_LVL] is null and IFAF_MOTHER_GRADE_LVL is null and [IRES_SPECIAL_CIRCUM_FLAG] = 1 then 'First-Gen'
				when [IFAF_FATHER_GRADE_LVL] is null and IFAF_MOTHER_GRADE_LVL is null and ([IRES_SPECIAL_CIRCUM_FLAG] != 1 or [IRES_SPECIAL_CIRCUM_FLAG] is null) then 'Unknown'
		  		when [IFAF_FATHER_GRADE_LVL] like '%Unknown%' and IFAF_MOTHER_GRADE_LVL like '%Unknown%' and [IRES_SPECIAL_CIRCUM_FLAG] = 1 then 'First-Gen'
				when [IFAF_FATHER_GRADE_LVL] like '%Unknown%' and IFAF_MOTHER_GRADE_LVL like '%Unknown%'  and ([IRES_SPECIAL_CIRCUM_FLAG] != 1 or [IRES_SPECIAL_CIRCUM_FLAG] is null) then 'Unknown'
		  		when [IFAF_FATHER_GRADE_LVL] not like 'College%' and IFAF_MOTHER_GRADE_LVL is null then 'First-Gen'
		  		when [IFAF_Mother_GRADE_LVL] not like 'College%' and IFAF_Father_GRADE_LVL is null then 'First-Gen'
		  		when [IFAF_FATHER_GRADE_LVL] like 'College%' and IFAF_MOTHER_GRADE_LVL like 'College%' then 'Both Parents College'
		  		when [IFAF_FATHER_GRADE_LVL] like 'College%' or IFAF_MOTHER_GRADE_LVL like 'College%' then 'One Parent College'
		  		when [IFAF_FATHER_GRADE_LVL] not like 'College%' and IFAF_MOTHER_GRADE_LVL not like 'College%' then 'First-Gen'
		   end as FIRST_GEN
		   ,case when [IFAF_FATHER_GRADE_LVL] is null and IFAF_MOTHER_GRADE_LVL is null and [IRES_SPECIAL_CIRCUM_FLAG] = 1 then 'First-Gen'
				when [IFAF_FATHER_GRADE_LVL] is null and IFAF_MOTHER_GRADE_LVL is null and ([IRES_SPECIAL_CIRCUM_FLAG] != 1 or [IRES_SPECIAL_CIRCUM_FLAG] is null) then 'Unknown'
		  		when [IFAF_FATHER_GRADE_LVL] like '%Unknown%' and IFAF_MOTHER_GRADE_LVL like '%Unknown%' and [IRES_SPECIAL_CIRCUM_FLAG] = 1 then 'First-Gen'
				when [IFAF_FATHER_GRADE_LVL] like '%Unknown%' and IFAF_MOTHER_GRADE_LVL like '%Unknown%'  and ([IRES_SPECIAL_CIRCUM_FLAG] != 1 or [IRES_SPECIAL_CIRCUM_FLAG] is null) then 'Unknown'
		  		when [IFAF_FATHER_GRADE_LVL] not like 'College%' and IFAF_MOTHER_GRADE_LVL is null then 'First-Gen'
		  		when [IFAF_Mother_GRADE_LVL] not like 'College%' and IFAF_Father_GRADE_LVL is null then 'First-Gen'
		  		when [IFAF_FATHER_GRADE_LVL] like 'College%' and IFAF_MOTHER_GRADE_LVL like 'College%' then 'Not First-Gen'
		  		when [IFAF_FATHER_GRADE_LVL] like 'College%' or IFAF_MOTHER_GRADE_LVL like 'College%' then 'Not First-Gen'
		  		when [IFAF_FATHER_GRADE_LVL] not like 'College%' and IFAF_MOTHER_GRADE_LVL not like 'College%' then 'First-Gen'
		   end as FIRST_GEN_CAT
	  FROM [FAFSA] a
	) isir
where rn = 1
)

SELECT
CensusTerm
--,[Program ID]
--,Program
--,Division
,[PELL+First-Gen]
,total
,retained 
,cast(retained/total as decimal(10,4)) 'retention rate'

FROM (
		SELECT
		CensusTerm
		--,[Program ID]
		--,Program
		--,Division
		,[PELL+First-Gen]
		,cast(COUNT([Student ID]) as decimal) as total
		,cast(sum(case when Retention = 'Retained' then 1 else 0 end) as decimal) retained

		FROM (
				SELECT 
				CensusTerm
				,[Student ID]
				--,[Program ID]
				--,Program
				--,Division
				,[PELL+First-Gen]
				,Retention

				From (
						SELECT DISTINCT a.[CensusYear]
							  ,a.[CensusTerm]
							  ,case when ret1.CensusTerm is not null then 'Retained' else 'Not Retained' end as 'Retention'
							  ,a.[CensusType]
							  ,a.[Student ID]
							  --,case when CTE.FIRST_GEN is null then 'Unknown' else CTE.FIRST_GEN end as FIRST_GEN
							  ,case when TA_AWARD_ID is not null and FG_CTE.FIRST_GEN = 'First-Gen' then 'Pell + First-Gen'
								    when TA_AWARD_ID is not null then 'Only PELL'
								    when FG_CTE.FIRST_GEN = 'First-Gen' then 'Only First-Gen'
								    when TA_AWARD_ID is null and (FG_CTE.FIRST_GEN is null or FG_CTE.FIRST_GEN = 'Unknown') then 'Unknown'
								    else 'not PELL or First-Gen'
								    end as 'PELL+First-Gen'
							  ,a.[Last Name]
							  ,a.[First Name]
							  ,a.[MI]
							  ,a.[Reg Cr]
							  ,a.[Load]
							  --,a.[Program]
							  --,a.[Program ID]
							  --,a.Division
							  ,a.[Admit Status]
							  ,a.[Stu Current Type]
							  ,a.[Class Level]
							  ,a.[Admit Term]
							  ,a.[Gender]
						  FROM [[CST_Combined_Census] a
						  LEFT JOIN (select distinct [Student ID], CensusTerm, CensusYear FROM CST_Combined_Census where CensusTerm like 'FA%') ret1 
									on a.[Student ID]+'*'+cast(left(a.CensusYear,4)+1 as varchar) = ret1.[Student ID]+'*'+cast(left(ret1.CensusYear,4) as varchar)
						  LEFT JOIN SPT_TA_ACYR z ON a.[Student ID]+'*'+a.CensusTerm = TA_STUDENT_ID+'*'+TA_TERM_ID and TA_AWARD_ID = 'PELL' and (TA_TERM_ACTION is null or TA_TERM_ACTION != 'C')
						  LEFT JOIN FG_CTE ON FG_CTE.FG_CTE_IDX = a.[Student ID]+'*'+left(a.CensusYear,4)
						  Where 
								a.CensusTerm like 'FA%' 
								and a.CensusTerm = a.[Admit Term]
								and a.[Admit Status] like '%Freshman%'
								and a.[Admit Status] not like 'Re-Admit'
								and a.[Program ID] != 'NONMATRIC.UG'
				) RET
		) RETENTION
		group by CensusTerm, [PELL+First-Gen]
	) MATH
	group by CensusTerm,  [PELL+First-Gen], total, retained
	Order by [PELL+First-Gen], CensusTerm asc
		  --Order by a.CensusYear, a.CensusTerm, a.CensusType, a.[Student ID]
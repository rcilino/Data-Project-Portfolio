SELECT
CensusTerm
--,[Program ID]
--,Program
--,Division
,total
,retained 
,[Gender]
,cast(retained/total as decimal(10,4)) 'retention rate'
FROM (
		SELECT
		CensusTerm
		--,[Program ID]
		--,Program
		--,Division
		,[Gender]
		,cast(COUNT([Student ID]) as decimal) as total
		,cast(sum(case when Retention = 'Retained' then 1 else 0 end) as decimal) retained
		FROM (
				SELECT 
				CensusTerm
				,[Student ID]
				--,[Program ID]
				--,Program
				--,Division
				,[Gender]
				,Retention
				From (
						SELECT DISTINCT a.[CensusYear]
							  ,a.[CensusTerm]
							  ,case when ret1.CensusTerm is not null then 'Retained' 
									when cred.ACAD_DEGREE_DATE is not null then 'Retained' else 'Not Retained' end as 'Retention'
							  ,cred.ACAD_DEGREE_DATE AS 'grad'
							  ,a.[Day10Type]
							  ,a.[Student ID]
							  ,a.[Last Name]
							  ,a.[First Name]
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
							  ,a.[IPEDS Desc]
							  ,a.[Term Status]
						  FROM [database].[dbo].[combined)Census_file_table] a
						  --LEFT JOIN K10_ACAD_PROGRAMS p ON a.[Program ID] = p.ACAD_PROGRAMS_ID
						  LEFT JOIN (select distinct [Student ID], CensusTerm, CensusYear FROM combined)Census_file_table where CensusTerm like 'FA%') ret1 
									on a.[Student ID]+'*'+cast(left(a.CensusYear,4)+1 as varchar) = ret1.[Student ID]+'*'+cast(left(ret1.CensusYear,4) as varchar)
						  LEFT JOIN ODS_ACAD_CREDENTIALS cred on a.[Student ID] = cred.ACAD_PERSON_ID and cred.ACAD_INSTITUTIONS_ID = 'xxxxxx' and cred.ACAD_ACAD_LEVEL = 'UG'
											 and ((Year(cred.ACAD_DEGREE_DATE) = cast(left(a.CensusYear,4)+1 as varchar) and Month(cred.ACAD_DEGREE_DATE) <=8)
												  or (Year(cred.ACAD_DEGREE_DATE) = cast(left(a.CensusYear,4) as varchar) and Month(cred.ACAD_DEGREE_DATE) between 9 and 12)
												 )
						  Where 
								a.CensusTerm like 'FA%' 
								and a.CensusTerm = a.[Admit Term]
								and a.[Admit Status] like '%Freshman%'
								and a.[Admit Status] not like 'Re-Admit'
								and a.[Program ID] != 'NONMATRIC.UG'
								--and a.CensusTerm not in ('FA2014')
								--and a.[Program ID] IN ('BIOCHEM.BA','BIO.ORG.BA','BIO.BIOMED.BA','MEDTECH.BS')
				) RET
		) RETENTION
		group by CensusTerm, [Gender]
	) MATH
	group by CensusTerm, [Gender], total, retained
	Order by [Gender], CensusTerm
		  --Order by a.CensusYear, a.CensusTerm, a.Day10Type, a.[Student ID]
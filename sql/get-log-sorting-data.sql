with
  log_data as (
    select
      datepart(year, cast(ScanningDateTime as date)) as [year],
      datepart(week, cast(ScanningDateTime as date)) as [week],
      Species as [species],
      SortingLength as [sorting_length],
      LengthModule as [length_module],
      SortingDiameterUnderBark as [sorting_diameter_under_bark],
      LogId as [log_id]
    from
      MAPPTVR.dbo.TimberLogInTvr2
    where
      cast(ScanningDateTime as date) > '2022-11-01'
  ),
  aggregated as (
    select
      [year],
      [week],
      [species],
      [sorting_length],
      min([length_module]) as [length_module],
      [sorting_diameter_under_bark],
      count(distinct [log_id]) as [logs]
    from
      log_data
    group by
      [year],
      [week],
      [species],
      [sorting_length],
      [sorting_diameter_under_bark]
  )
select *
from aggregated
order by
  [year],
  [week],
  [species],
  [sorting_length],
  [sorting_diameter_under_bark]

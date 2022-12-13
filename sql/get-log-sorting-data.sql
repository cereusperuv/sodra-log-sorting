with
  log_data as (
    select
      datepart(year, cast(ScanningDateTime as date)) as [year],
      datepart(week, cast(ScanningDateTime as date)) as [week],
      [Species] as [species],
      [LogId] as [log_id],
      cast([SortingLength] as int) as [sorting_length],
      cast([SortingDiameterUnderBark] as int) as [sorting_diameter_under_bark],
      [RealVolumeUnderBark] as [real_volume_under_bark]
    from
      MAPPTVR.dbo.TimberLogInTvr2
    where
      cast(ScanningDateTime as date) > '2022-11-01'
  ),
  aggregated_by_diameter_and_length as (
    select
      [year],
      [week],
      [species],
      [sorting_length],
      [sorting_diameter_under_bark],
      count(distinct [log_id]) as [logs],
      sum([real_volume_under_bark]) as [volume_m3fub]
    from
      log_data
    group by
      [year],
      [week],
      [species],
      [sorting_length],
      [sorting_diameter_under_bark]
  ),
  diameter_group_a as (
    select
      [year],
      [week],
      [species],
      'a' as [diameter_group],
      case
        when (
          [sorting_length] >= 300 and
          [sorting_length] < 366
        ) then '300-365'
        when (
          [sorting_length] >= 366 and
          [sorting_length] < 376
        ) then '366-375'
        when (
          [sorting_length] >= 376 and
          [sorting_length] < 476
        ) then '376-475'
        when (
          [sorting_length] >= 476 and
          [sorting_length] < 486
        ) then '476-485'
        when (
          [sorting_length] >= 4860 and
          [sorting_length] < 4960
        ) then '486-495'
        when (
          [sorting_length] >= 496 and
          [sorting_length] < 536
        ) then '496-535'
        when (
          [sorting_length] >= 536 and
          [sorting_length] < 546
        ) then '536-545'
        when (
          [sorting_length] >= 546 and
          [sorting_length] < 556
        ) then '546-555'
        when (
          [sorting_length] >= 556 and
          [sorting_length] <= 650
        ) then '556-650'
        else '-'
      end as [length_interval],
      [logs],
      [volume_m3fub]
    from
      aggregated_by_diameter_and_length
    where
      [sorting_diameter_under_bark] >= 160 and
      [sorting_diameter_under_bark] < 210
  ),
  diameter_group_b as (
    select
      [year],
      [week],
      [species],
      'b' as [diameter_group],
      case
        when (
          [sorting_length] >= 300 and
          [sorting_length] < 366
        ) then '300-365'
        when (
          [sorting_length] >= 366 and
          [sorting_length] < 376
        ) then '366-375'
        when (
          [sorting_length] >= 376 and
          [sorting_length] < 476
        ) then '376-475'
        when (
          [sorting_length] >= 476 and
          [sorting_length] < 486
        ) then '476-485'
        when (
          [sorting_length] >= 4860 and
          [sorting_length] < 4960
        ) then '486-495'
        when (
          [sorting_length] >= 496 and
          [sorting_length] < 536
        ) then '496-535'
        when (
          [sorting_length] >= 536 and
          [sorting_length] < 546
        ) then '536-545'
        when (
          [sorting_length] >= 546 and
          [sorting_length] < 556
        ) then '546-555'
        when (
          [sorting_length] >= 556 and
          [sorting_length] <= 650
        ) then '556-650'
        else '-'
      end as [length_interval],
      [logs],
      [volume_m3fub]
    from
      aggregated_by_diameter_and_length
    where
      [sorting_diameter_under_bark] >= 210 and
      [sorting_diameter_under_bark] <= 390
  ),
  combined as (
    select *
    from diameter_group_a
    union all
    select *
    from diameter_group_b
  ),
  aggregated as (
    select
      [year],
      [week],
      [species],
      [diameter_group],
      [length_interval],
      sum([logs]) as [logs],
      sum([volume_m3fub]) as [volume_m3fub]
    from
      combined
    group by
      [year],
      [week],
      [species],
      [diameter_group],
      [length_interval]
  )
select *
from aggregated
order by
  [year],
  [week],
  [species],
  [diameter_group],
  [length_interval]

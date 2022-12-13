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
      cast(ScanningDateTime as date) >= '{{ start_date }}' {% if end_date -%} 
      and
      cast(ScanningDateTime as date) <= '{{ end_date }}'
      {%- endif %}
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
  {%- for group in diameter_groups %}
  diameter_group_{{ group["name"] }} as (
    select
      [year],
      [week],
      [species],
      '{{ group["name"] }}' as [diameter_group],
      case
        {% for l in group["length_intervals"] -%}
        when (
          [sorting_length] >= {{ l.split("-")[0] }} and
          [sorting_length] < {{ l.split("-")[1]|int + 1 }}
        ) then '{{ l }}'
        {% endfor -%}
        else '-'
      end as [length_interval],
      [logs],
      [volume_m3fub]
    from
      aggregated_by_diameter_and_length
    where
      [sorting_diameter_under_bark] {% if group["inclusive"] in ["left", "both"] -%}
      >= {%- else -%} > {%- endif %} {{ group["from"] }} and
      [sorting_diameter_under_bark] {% if group["inclusive"] in ["right", "both"] -%}
      <= {%- else -%} < {%- endif %} {{ group["to"] }}
  ),
  {%- endfor %}
  combined as (
    {% for group in diameter_groups -%}
    select *
    from diameter_group_{{ group["name"] }}
    {%- if not loop.last %}
    union all
    {% endif -%}
    {%- endfor %}
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

with
  log_data as (
    select
      cast(ScanningDateTime as date) as [date],
      [Species] as [species],
      [LotId] as [lot_id],
      [LogId] as [log_id],
      cast([SortingLength] as int) as [sorting_length],
      cast([SortingDiameterUnderBark] as int) as [sorting_diameter_under_bark],
      [RealVolumeUnderBark] as [real_volume_under_bark]
    from
      MAPPTVR.dbo.TimberLogInTvr2
    where
      [Species] = {{ species }} and
      cast([ScanningDateTime] as date) >= '{{ start_date }}' {% if end_date -%} 
      and
      cast([ScanningDateTime] as date) <= '{{ end_date }}'
      {%- endif %}
  ),
  aggregated_by_diameter_and_length as (
    select
      [date],
      [species],
      [lot_id],
      [sorting_length],
      [sorting_diameter_under_bark],
      count(distinct [log_id]) as [logs],
      sum([real_volume_under_bark]) as [volume_m3fub]
    from
      log_data
    group by
      [date],
      [species],
      [lot_id],
      [sorting_length],
      [sorting_diameter_under_bark]
  ),
  {%- for group in diameter_groups %}
  diameter_group_{{ group["diameter_interval"][0] }} as (
    select
      [date],
      [species],
      [lot_id],
      '{{ group["diameter_group"] }}' as [diameter_group],
      case
        {% for l in group["length_interval"] -%}
        when (
          [sorting_length] >= {{ l[0] }} {%- if not loop.last %} and
          [sorting_length] < {{ l[1] }} {%- endif %}
        ) then cast({{ l[0] }}/10.0 as decimal(3, 1))
        {% endfor -%}
      end as [length],
      [logs],
      [volume_m3fub]
    from
      aggregated_by_diameter_and_length
    where
      [sorting_diameter_under_bark] >= {{ group["diameter_interval"][0] }}
      {%- if not loop.last %} and
      [sorting_diameter_under_bark] < {{ group["diameter_interval"][1] }}
      {%- endif %}
  ),
  {%- endfor %}
  combined as (
    {% for group in diameter_groups -%}
    select *
    from diameter_group_{{ group["diameter_interval"][0] }}
    {%- if not loop.last %}
    union all
    {% endif -%}
    {%- endfor %}
  ),
  aggregated as (
    select
      [date],
      [species],
      [lot_id],
      [diameter_group],
      [length],
      sum([logs]) as [logs],
      sum([volume_m3fub]) as [volume_m3fub]
    from
      combined
    group by
      [date],
      [species],
      [lot_id],
      [diameter_group],
      [length]
  )
select *
from aggregated
order by
  [date],
  [species],
  [lot_id],
  [diameter_group],
  [length]

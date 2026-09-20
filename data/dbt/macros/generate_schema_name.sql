{# WarehouseReader (backend/app/infrastructure/warehouse/reader.py) queries bare `staging.*`
   and `marts.*` schemas. dbt's default generate_schema_name prefixes a custom +schema with the
   target schema (e.g. "main_marts"); override it so the custom schema is used as-is. #}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}

WITH
  -- @see https://www.postgresql.org/docs/9.5/static/catalog-pg-namespace.html
  namespace AS (
    SELECT 'namespace' AS "type", oid AS "id", nspname AS "name"
    FROM pg_catalog.pg_namespace
    WHERE nspname NOT IN ('information_schema') and nspname NOT ILIKE 'pg_%'
    ORDER BY nspname
  ),
  -- @see https://www.postgresql.org/docs/9.5/static/catalog-pg-class.html
  -- rekind  r = ordinary table, i = index, S = sequence, v = view, m = materialized view, c = composite type, t = TOAST table, f = foreign table
  -- relpersistence -- p = permanent table, u = unlogged table, t = temporary table
  class AS (
    SELECT
      'class' AS "type",
      oid AS "id",
      relname AS "name",
      relnamespace AS "namespace_id",
      reltype AS "type_id",
      relkind as "kind"
      --,
      --(pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00010000') = B'00010000' AS "insertable",
      --(pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00001000') = B'00001000' AS "updatable",
      --(pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00000100') = B'00000100' AS "deletable"
    FROM pg_catalog.pg_class
    WHERE relnamespace in (SELECT "id" FROM namespace)
      and relpersistence in ('p')
      and relkind in ('r', 'v', 'm', 'c', 'f')
    ORDER BY relnamespace, relname
  ),
  -- @see https://www.postgresql.org/docs/9.5/static/catalog-pg-attribute.html
  attribute AS (
    SELECT
      'attribute' AS "type",
      a.attrelid AS "class_id",
      a.attnum AS "num",
      a.attname AS "name",
      a.atttypid AS "type_id",
      a.attnotnull AS "notnull",
      a.atthasdef AS "hasdefault",
      pg_catalog.format_type(a.atttypid, a.atttypmod) as stype,
      d.adsrc AS svalue
    FROM pg_catalog.pg_attribute a
    LEFT JOIN pg_catalog.pg_attrdef d ON (a.attrelid, a.attnum)
                                     = (d.adrelid,  d.adnum)

    WHERE attrelid in (SELECT "id" FROM class) AND attnum > 0 AND NOT attisdropped
    ORDER BY attrelid, attnum
  ),
  -- contype c = check constraint, f = foreign key constraint, p = primary key constraint, u = unique constraint, t = constraint trigger, x = exclusion constraint
  "constraint" as (
    SELECT
      'constraint' as "type",
      conname as "name",
      contype as "kind",
      conrelid as "class_id",
      nullif(confrelid, 0) as "fclass_id",
      conkey,
      confkey
   FROM pg_catalog.pg_constraint
   WHERE
	conrelid in (select "id" from class) AND
	contype in ('f', 'p', 'u') AND
	CASE WHEN contype = 'f' THEN confrelid in (SELECT "id" FROM class) ELSE TRUE END
  ),
  type as (
    SELECT
      'type' AS "type",
      oid as id,
      typname as name,
      typnamespace as namespace_id,
      typtype as kind,
      typcategory as category
    FROM
       pg_catalog.pg_type
    WHERE
       oid IN (SELECT type_id FROM class) OR
       oid IN (SELECT type_id FROM attribute)
     ORDER BY namespace_id, name
  ),
 enums as (
    SELECT
      'enum' AS "type",
      e.oid as id,
      t.oid as type_id,
      t.typname as name,
      t.typnamespace as namespace_id,
      e.enumlabel as label
    FROM
       pg_catalog.pg_type t
       LEFT JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
    WHERE
       t.typtype = 'e' AND t.oid IN (SELECT type_id FROM attribute)
    ORDER BY namespace_id, name, label
)
SELECT row_to_json(x) AS object FROM namespace AS x
UNION ALL
SELECT row_to_json(x) AS object FROM "type" AS x
UNION ALL
SELECT row_to_json(x) AS object FROM "enums" AS x
UNION ALL
SELECT row_to_json(x) AS object FROM "constraint" AS x
UNION ALL
SELECT row_to_json(x) AS object FROM class AS x
UNION ALL
SELECT row_to_json(x) AS object FROM attribute AS x

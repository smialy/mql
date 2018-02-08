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
      'table' AS "type",
      oid AS "id",
      relname AS "name",
      relnamespace AS "namespaceid",
      reltype AS "typeid",
      relkind not in ('i', 'c') AS "selectable",
      (pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00010000') = B'00010000' AS "insertable",
      (pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00001000') = B'00001000' AS "updatable",
      (pg_catalog.pg_relation_is_updatable(oid, true)::bit(8) & B'00000100') = B'00000100' AS "deletable"
    FROM pg_catalog.pg_class
    WHERE relnamespace in (SELECT "id" FROM namespace) and relpersistence in ('p') and relkind in ('r', 'v', 'm', 'c', 'f')
    ORDER BY relnamespace, relname
  ),
  -- @see https://www.postgresql.org/docs/9.5/static/catalog-pg-attribute.html
  attribute AS (
    SELECT
      'attribute' AS "type",
      attrelid AS "classid",
      attnum AS "num",
      attname AS "name",
      atttypid AS "typeid",
      attnotnull AS "isnotnull",
      atthasdef AS "hasdefault"
    FROM pg_catalog.pg_attribute
    WHERE attrelid in (SELECT "id" FROM class) AND attnum > 0 AND NOT attisdropped
    ORDER BY attrelid, attnum
  ),
  -- contype c = check constraint, f = foreign key constraint, p = primary key constraint, u = unique constraint, t = constraint trigger, x = exclusion constraint
  "constraint" as (
    SELECT
      'constraint' as "type",
      conname as "name",
      contype as "type",
      conrelid as "classid",
      nullif(confrelid, 0) as "fclassid"
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
      typnamespace as namespaceid,
      typtype as kind,
      typcategory as category

    FROM
       pg_catalog.pg_type
    WHERE
       oid IN (SELECT typeid FROM class) OR
       oid IN (SELECT typeid FROM attribute)
     ORDER BY namespaceid, name
  )
SELECT row_to_json(x) AS object FROM namespace AS x
UNION ALL
SELECT row_to_json(x) AS object FROM "type" AS x
UNION ALL
SELECT row_to_json(x) AS object FROM class AS x
UNION ALL
SELECT row_to_json(x) AS object FROM attribute AS x
UNION ALL
SELECT row_to_json(x) AS object FROM "constraint" AS x

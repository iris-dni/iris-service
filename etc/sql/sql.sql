CREATE TABLE petitions (
    id LONG PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP,
        effective TIMESTAMP,
        expires TIMESTAMP
    ),
    state STRING,
    tags ARRAY(STRING),
    title STRING INDEX OFF,
    -- relation to cities table
    city STRING,
    type STRING,
    description STRING INDEX OFF,
    suggested_solution STRING INDEX OFF,

    -- relations for files table
    images ARRAY(STRING),
    -- relations to locations table
    links ARRAY(STRING),
    -- relations to files table,
    videos ARRAY(STRING),
    -- relations to locations table
    connected_locations ARRAY(STRING),

    signatures OBJECT(STRICT) AS (
        amount LONG,
        required LONG
    ),

    owner STRING,
    response_token STRING,

    db_class__ STRING INDEX OFF
)
CLUSTERED INTO 5 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');

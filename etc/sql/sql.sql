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
    title STRING,
    city STRING,
    type STRING,
    description STRING INDEX OFF,
    suggested_solution STRING INDEX OFF,

    images ARRAY(STRING),
    links ARRAY(STRING),
    videos ARRAY(STRING),
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

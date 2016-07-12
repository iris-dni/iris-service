CREATE TABLE petitions (
    id LONG PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP,
        effective TIMESTAMP,
        expires TIMESTAMP
    ),
    state STRING,
    db_class__ STRING INDEX OFF
)
CLUSTERED INTO 5 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');

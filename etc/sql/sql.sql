CREATE ANALYZER edge_ngram_fulltext (
    TOKENIZER t with (
        type='edgeNGram',
        min_gram=2,
        max_gram=10,
        token_chars=['letter', 'digit']
    ),
    TOKEN_FILTERS (
        standard,
        lowercase
    )
);

CREATE ANALYZER email_ngram_fulltext (
    TOKENIZER t with (
        type='edgeNGram',
        min_gram=3,
        max_gram=10,
        token_chars=['letter', 'digit']
    ),
    TOKEN_FILTERS (
        standard,
        lowercase
    )
);


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

    supporters OBJECT(STRICT) AS (
        amount LONG,
        required LONG
    ),

    owner STRING,
    response_token STRING,

    INDEX tags_ft
      USING FULLTEXT(description)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX title_ft
      USING FULLTEXT(description)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX description_ft
      USING FULLTEXT(description)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX suggested_solution_ft
      USING FULLTEXT(suggested_solution)
      WITH (ANALYZER = 'edge_ngram_fulltext')
)
CLUSTERED INTO 5 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');


CREATE TABLE users (
    id LONG PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP
    ),
    state STRING,

    email STRING,
    firstname STRING,
    lastname STRING,

    roles ARRAY(STRING),

    sso ARRAY(
        OBJECT(STRICT) AS (
            provider STRING,
            trusted BOOLEAN
        )
    ),

    INDEX firstname_ft
      USING FULLTEXT(firstname)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX lastname_ft
      USING FULLTEXT(lastname)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX email_ft
      USING FULLTEXT(email)
      WITH (ANALYZER = 'email_ngram_fulltext')
)
CLUSTERED INTO 5 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');


CREATE TABLE ssotokens (
    token STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP
    ),
    sso STRING INDEX OFF,
    apikey STRING INDEX OFF
)
CLUSTERED INTO 5 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');


CREATE TABLE lc_iidsequences (
    iid LONG
)
CLUSTERED INTO 1 SHARDS
          WITH (number_of_replicas='0-all',
                column_policy='strict');

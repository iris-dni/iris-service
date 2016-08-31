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
    id STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP,
        effective TIMESTAMP,
        expires TIMESTAMP
    ),
    state OBJECT(IGNORED) AS (
        name STRING,
        parent STRING,
        listable BOOLEAN,
        timer LONG
    ),
    tags ARRAY(STRING),
    title STRING INDEX OFF,
    city_answer STRING INDEX OFF,
    type STRING,
    description STRING INDEX OFF,
    suggested_solution STRING INDEX OFF,

    supporters OBJECT(STRICT) AS (
        amount LONG,
        required LONG
    ),

    response_token STRING,

    relations OBJECT(STRICT) AS (
        -- the owner relation
        owner STRING,
        -- the city relation
        city STRING,

        images ARRAY(
            OBJECT(STRICT) AS (
                id STRING,
                state string
            )
        ),
        videos ARRAY(
            OBJECT(STRICT) AS (
                id STRING,
                state string
            )
        ),
        links ARRAY(
            OBJECT(STRICT) AS (
                id STRING,
                state string
            )
        ),
        connected_locations ARRAY(
            OBJECT(STRICT) AS (
                id STRING,
                state string
            )
        )
    ),

    INDEX tags_ft
      USING FULLTEXT(tags)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX title_ft
      USING FULLTEXT(title)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX description_ft
      USING FULLTEXT(description)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX suggested_solution_ft
      USING FULLTEXT(suggested_solution)
      WITH (ANALYZER = 'edge_ngram_fulltext')
)
CLUSTERED INTO {{ Petition.shards }} SHARDS
          WITH (number_of_replicas='{{ Petition.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE supporters (
    id STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP
    ),
    phone_user OBJECT(IGNORED) AS (
        telephone STRING,
        firstname STRING,
        lastname STRING
    ),

    relations OBJECT(STRICT) AS (
        -- the user relation
        user STRING,
        -- the petition relation
        petition STRING
    )
)
CLUSTERED INTO {{ Supporters.shards }} SHARDS
          WITH (number_of_replicas='{{ Supporters.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE files (
    id STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP
    ),
    state STRING
)
CLUSTERED INTO {{ File.shards }} SHARDS
          WITH (number_of_replicas='{{ File.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE weblocations (
    id STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP
    ),
    state STRING,
    url STRING INDEX OFF,
    og OBJECT(STRICT) AS (
        url STRING INDEX OFF,
        title STRING,
        site_name STRING,
        description STRING INDEX OFF,
        image STRING INDEX OFF,
        video STRING INDEX OFF
    )
)
CLUSTERED INTO {{ WebLocation.shards }} SHARDS
          WITH (number_of_replicas='{{ WebLocation.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE cities (
    id STRING PRIMARY KEY,
    state STRING,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP,
        modified TIMESTAMP
    ),
    name STRING,
    tags ARRAY(STRING),
    zips ARRAY(STRING),
    treshold LONG,
    provider STRING,
    contact OBJECT(STRICT) AS (
        salutation STRING,
        address STRING
    ),

    INDEX tags_ft
      USING FULLTEXT(tags)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX name_ft
      USING FULLTEXT(name)
      WITH (ANALYZER = 'edge_ngram_fulltext'),
    INDEX zips_ft
      USING FULLTEXT(zips)
      WITH (ANALYZER = 'edge_ngram_fulltext')
)
CLUSTERED INTO {{ Cities.shards }} SHARDS
          WITH (number_of_replicas='{{ Cities.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE users (
    id STRING PRIMARY KEY,
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
CLUSTERED INTO {{ Users.shards }} SHARDS
          WITH (number_of_replicas='{{ Users.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE ssotokens (
    token STRING PRIMARY KEY,
    dc OBJECT(STRICT) AS (
        created TIMESTAMP
    ),
    sso STRING INDEX OFF,
    apikey STRING INDEX OFF
)
CLUSTERED INTO {{ SSOTokens.shards }} SHARDS
          WITH (number_of_replicas='{{ SSOTokens.number_of_replicas }}',
                column_policy='strict');


CREATE TABLE lovely_essequences (
    name STRING PRIMARY KEY,
    iid LONG
)
CLUSTERED INTO {{ Lovely_ESSequences.shards }} SHARDS
          WITH (number_of_replicas='{{ Lovely_ESSequences.number_of_replicas }}',
                column_policy='strict');


SETTINGS = {
    "local": {
        "hosts": "localhost",
        "crate_host": "http://localhost:8042",
        "sql_settings": "sql/sql"
    },
    "dev": {
        "hosts": "ap1.iris-dev.ls.af",
        "crate_host": "http://ap1.azdev.ls.af:4200",
        "sql_settings": "sqldev"
    },
    "staging": {
        "hosts": "ap1.iris-stg.ls.af",
        "crate_host": "http://ap1.azstaging.ls.af:4200",
        "sql_settings": "sqldev"
    },
    "production": {
        "hosts": "ap1.iris-prod.ls.af",
        "crate_host": "http://ap10.az.ls.af:4200",
        "sql_settings": "sqlproduction"
    }
}

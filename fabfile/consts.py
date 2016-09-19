
SETTINGS = {
    "local": {
        "hosts": "localhost",
        "crate_host": "http://localhost:8042",
        "sql_settings": "sql/sql"
    },
    "dev": {
        "hosts": "st1.p.ls.af",
        "crate_host": "http://st1.p.ls.af:10042",
        "sql_settings": "sql/sql"
    },
    "staging": {
        "hosts": "st4.p.ls.af",
        "crate_host": "http://st4.p.ls.af:11042",
        "sql_settings": "sql/sql"
    },
    "production": {
        "hosts": "st1.p.ls.af",
        "crate_host": "http://st1.p.ls.af:12042",
        "sql_settings": "sql/sql"
    }
}

CREATE TABLE IF NOT EXISTS unpd (
    id serial PRIMARY KEY,
    user_name varchar NOT NULL,
    domain_name varchar NOT NULL DEFAULT '',
    password varchar NOT NULL DEFAULT '',
    event_name varchar NOT NULL DEFAULT '',
    counts int NOT NULL
);

CREATE INDEX IF NOT EXISTS unpd_user_name_index ON unpd(user_name);
CREATE INDEX IF NOT EXISTS unpd_domain_name_index on unpd(domain_name);
CREATE INDEX IF NOT EXISTS unpd_domain_name_index on unpd(password);
CREATE INDEX IF NOT EXISTS unpd_event_name_index ON unpd(event_name);

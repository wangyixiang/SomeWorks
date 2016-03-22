CREATE TABLE IF NOT EXISTS files (
    id serial PRIMARY KEY,
    absolute_name varchar NOT NULL,
    unc_name varchar NOT NULL DEFAULT '',
    basename varchar NOT NULL,
    dir_name varchar NOT NULL,
    owner_name varchar NOT NULL DEFAULT '',
    domain_name varchar NOT NULL DEFAULT '',
    last_modified_time timestamp NOT NULL,
    file_size bigint NOT NULL,
    is_file boolean NOT NULL DEFAULT TRUE,
    is_exists boolean NOT NULL DEFAULT TRUE,
    os varchar NOT NULL DEFAULT 'windows',
    UNIQUE(absolute_name)
);
CREATE INDEX IF NOT EXISTS files_absolute_name_index ON files(absolute_name);
CREATE INDEX IF NOT EXISTS files_basename_index ON files(basename);
CREATE INDEX IF NOT EXISTS files_dir_name_index ON files(dir_name);
CREATE INDEX IF NOT EXISTS files_owner_name_index ON files(owner_name);
CREATE INDEX IF NOT EXISTS files_domain_name_index on files(domain_name);
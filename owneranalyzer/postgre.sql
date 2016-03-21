CREATE TABLE files (
    id serial PRIMARY KEY,
    absolute_name varchar NOT NULL,
    unc_name varchar NOT NULL DEFAULT "",
    basename varchar NOT NULL,
    dirname varchar NOT NULL,
    ownername varchar NOT NULL DEFAULT "",
    domainname varchar NOT NULL DEFAULT "",
    last_modified_time timestamp NOT NULL,
    filesize bigint NOT NULL,
    is_file boolean NOT NULL DEFAULT TRUE,
    is_exists boolean NOT NULL DEFAULT TRUE,
    os varchar NOT NULL DEFAULT "windows",
    UNIQUE(absolute_name)
);
CREATE INDEX files_absolute_name_index ON files(absolute_name);
CREATE INDEX files_basename_index ON files(basename);
CREATE INDEX files_dir_name_index ON files(dirname);
CREATE INDEX files_ownername_index ON files(ownername);
CREATE INDEX files_domainname_index on files(domainname);
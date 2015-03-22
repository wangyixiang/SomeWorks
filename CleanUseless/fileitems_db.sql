CREATE USER fi_dba;
CREATE USER fi_user;
CREATE DATABASE fi_db WITH OWNER fi_dba;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO fi_user;
CREATE TABLE file_items (
    fi_id serial PRIMARY KEY,
    fi_absolute_name varchar NOT NULL,
    fi_unc_name varchar NOT NULL,
    fi_name varchar NOT NULL,
    fi_dir_name varchar NOT NULL,
    fi_last_modified_time timestamp NOT NULL,
    fi_size bigint NOT NULL,
    is_file boolean NOT NULL DEFAULT TRUE,
    is_exists boolean NOT NULL DEFAULT TRUE,
    UNIQUE(fi_unc_name)
);
CREATE INDEX file_items_fi_dir_name_index ON file_items(fi_dir_name);
CREATE INDEX file_items_fi_name_index ON file_items(fi_name);
CREATE TABLE "aggregates" (
    uuid varchar(36) NOT NULL PRIMARY KEY,
    version int NOT NULL DEFAULT 1
);

CREATE TABLE "events" (
    uuid varchar(36) NOT NULL PRIMARY KEY,
    aggregate_uuid varchar(36) NOT NULL REFERENCES "aggregates" ("uuid"),
    name varchar(50) NOT NULL,
    data json
);

CREATE INDEX aggregate_uuid_idx ON "events" ("aggregate_uuid");


create table appuser (
    id serial,
    handle varchar(64) unique,
    pwsalt varchar(32) not null,
    passwd varchar(32) not null,
    created integer not null default -1,
    flags integer not null default 0,
    role integer not null default 0
);

create table approle (
    id serial,
    name varchar(32) unique,
    flagval integer unique
);

insert into approle (name, flagval) values
    ('login', 1), ('admin', 128);

create table leak (
    id serial,
    title varchar(128) not null,
    description text,
    created integer,
    modified integer,
    flags integer not null default 0
);

select AddGeometryColumn('leak', 'location', 4326, 'POINT', 2);

insert into leak (title, description, location) values ('Test One', 'A test.', ST_GeomFromText('POINT(-71.0 42.0)',4326));

create table leakflag (
    id serial,
    name varchar(32) unique,
    flagval integer unique
);

insert into leakflag (name, flagval) values
    ('abuse', 2), ('review', 4);

create table leak_note (
    id serial,
    leak_id integer not null, -- constraint goes here
    created integer not null default -1,
    title varchar(128) not null,
    body text,
    flags integer not null default 0
);

create table noteflag (
    id serial,
    name varchar(32) unique,
    flagval integer unique
);

insert into noteflag (name, flagval) values
    ('abuse', 2);

-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create database tournament;

drop table match;
drop table player;

create table player (
id SERIAL primary key,
name text
);

create table match (
id1 integer references player(id),
id2 integer references player(id),
match SERIAL primary key
);

create table standings (
id integer references player(id),
match integer references match(match),
score integer
);

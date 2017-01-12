-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

create table player (
id SERIAL primary key,
name text
);

create table match (
winner integer references player(id),
loser integer references player(id),
match SERIAL primary key
);


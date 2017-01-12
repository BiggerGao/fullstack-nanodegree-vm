#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except Exception as e:
        raise e


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    query = "TRUNCATE match CASCADE;"
    cursor.execute(query)
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    query = "TRUNCATE player CASCADE;"
    cursor.execute(query)
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    query = "SELECT count(*) as num from player"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    db.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()
    query = "INSERT INTO player (name) values (%s);"
    param = (name,)
    cursor.execute(query, param)

    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()

    query = '''SELECT player.id, name, COALESCE(wins, 0) , COALESCE(matches, 0)
                from player left join
                ((SELECT id, count(*) as matches from player, match
                where player.id = match.loser
                OR player.id = match.winner
                group by player.id) as tm
                LEFT JOIN
                (SELECT winner as wid, count(*) as wins from match
                group by winner) as tw
                ON tw.wid = tm.id) as twm
                ON player.id = twm.id
                ORDER BY wins DESC
               '''
    cursor.execute(query)
    result = cursor.fetchall()

    db.close()
    return result


class match(object):
    """docstring for match"""
    def __init__(self, arg):
        super(match, self).__init__()
        self.arg = arg


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, cursor = connect()
    query = "insert into match (winner, loser) values (%s, %s)"
    param = (winner, loser)
    cursor.execute(query, param)
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db, cursor = connect()
    cursor = db.cursor()
    cursor.execute('''SELECT player.id, name, wins FROM player LEFT JOIN
        (SELECT winner, count(*) as wins from match group by winner) as tw
        ON player.id = tw.winner
        ORDER BY wins
        ''')
    result = cursor.fetchall()
    db.close()
    pairings = []
    for index in range(0, len(result), 2):
        item = (result[index][0], result[index][1],
                result[index+1][0], result[index+1][1])
        pairings.append(item)

    return pairings

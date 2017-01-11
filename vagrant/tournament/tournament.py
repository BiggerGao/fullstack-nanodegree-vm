#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute('''delete from standings;''')
    c.execute('''delete from match;''')
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute('''delete from player;''')
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute('''select count(*) as num from player''')
    count = c.fetchone()[0]
    conn.close()
    return count

def registerPlayer(name):
    """Adds a player to the tournament database.
    
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("insert into player (name) values (%s);", (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.
    
    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()

    c.execute('''
        SELECT player.id, name, COALESCE(wins, 0), COALESCE(matches, 0) FROM 
        player LEFT JOIN
        (SELECT id, count(*) AS matches, sum(score) AS wins FROM standings 
        GROUP BY id) AS st
        ON player.id = st.id
        ''')

    result = c.fetchall()
    conn.close()
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

    conn = connect()
    c = conn.cursor()

    c.execute("insert into match (id1, id2) values (%s, %s)", (winner, loser))
    conn.commit()
    c.execute("select match from match order by match DESC")
    match = c.fetchone()[0]
    c.execute("insert into standings (id, match, score) values (%s, %s, %s)", (winner, match, 1))
    c.execute("insert into standings (id, match, score) values (%s, %s, %s)", (loser, match, 0))
    conn.commit()
    conn.close()
 
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
    conn = connect()
    c = conn.cursor()
    c.execute('''SELECT player.id, name, COALESCE(wins, 0) as wins FROM 
        player LEFT JOIN
        (SELECT id, count(*) AS matches, sum(score) AS wins FROM standings 
        GROUP BY id) AS st
        ON player.id = st.id
        ORDER BY wins DESC''')
    result = c.fetchall()
    conn.close()
    pairings = []
    for index in range(0, len(result), 2):
        item = (result[index][0],result[index][1],result[index+1][0],result[index+1][1])
        pairings.append(item)

    return pairings

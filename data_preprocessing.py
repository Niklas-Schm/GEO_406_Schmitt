import pathlib
import pandas as pd
import sqlite3

# setup paths
current_directory = pathlib.Path(__file__).parent
data_path = current_directory / 'pegeldaten_th'
meta_data_path = data_path / 'pegel_th.xlsx'
db_path = current_directory / 'Geo_406_Schmitt.db'


def create_tables(connection, cursor):
    """
    Create necessary tables in the SQLite database if they do not exist.

    Args:
        cursor: Cursor object to execute SQL commands.
        :param cursor:
        :param connection:
    """
    cursor.execute('''CREATE TABLE IF NOT EXISTS pegel_q(
        messstelle_nr TEXT,
        zeit TEXT,
        q REAL,
        q_min REAL,
        q_max REAL
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pegel_w(
        messstelle_nr TEXT,
        zeit TEXT,
        w INTEGER,
        w_min INTEGER,
        w_max INTEGER
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pegel_meta(
        MesstellenNr INTEGER,
        Standort TEXT,
        Gewaesser TEXT,
        Einzugsgebiet_Oberirdisch REAL,
        Status INTEGER,
        Entfernung_Muendung REAL,
        Messnetz_Kurzname TEXT,
        Ostwert REAL,
        Nordwert REAL,
        MB INTEGER,
        MS1 INTEGER,
        MS2 INTEGER,
        MS3 INTEGER
        )''')

    connection.commit()


def clear_tabels(connection, cursor):
    """
    Clear the pegel_q and pegel_w tables in the SQLite database.

    Args:
        cursor: Cursor object to execute SQL commands.
        :param cursor:
        :param connection:
    """
    cursor.execute('''DELETE FROM pegel_q''')
    cursor.execute('''DELETE FROM pegel_w''')
    cursor.execute('''DELETE FROM pegel_meta''')
    connection.commit()

import pathlib
import pandas as pd
import sqlite3
import csv

# setup paths
current_directory = pathlib.Path(__file__).parent
data_path = current_directory / 'pegeldaten_th'
meta_data_path = data_path / 'pegel_th.xlsx'
db_path = current_directory / 'Geo_406_Schmitt.db'


def create_tables(connection, cursor):
    """
    Creates the necessary tables in the database if they don't already exist.

    Args:
        connection: A connection object to the database.
        cursor: A cursor object for executing SQL commands.
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
    Clears all data from the tables 'pegel_q', 'pegel_w', and 'pegel_meta' in the database.

    Args:
        connection: A connection object to the database.
        cursor: A cursor object for executing SQL commands.
    """
    cursor.execute('''DELETE FROM pegel_q''')
    cursor.execute('''DELETE FROM pegel_w''')
    cursor.execute('''DELETE FROM pegel_meta''')
    connection.commit()


def read_calc(path, art, connection, cursor):
    """
    Reads data from a file specified by the path, processes it, and inserts it into a database.

    Args:
        path (str): The path to the file containing the data.
        art (str): The type of data being processed ('q' or 'w').
        connection: A connection object to the database.
        cursor: A cursor object for executing SQL commands.

    Returns:
        tuple: A tuple containing the sum of values, the count of values, the maximum value,
               the minimum value, and the type of data processed (art).
    """
    min_wert = None
    max_wert = None
    if art == 'q':
        wert = 'q'
        min_wert = 'q_min'
        max_wert = 'q_max'
    elif art == 'w':
        wert = 'w'
        min_wert = 'w_min'
        max_wert = 'w_max'

    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  # Skip header
        data = [(row[0], row[1], float(row[5]) if row[5] != 'None' else None,
                 float(row[6]) if row[6] != 'None' else None,
                 float(row[7]) if row[7] != 'None' else None) for row in reader]

    cursor.executemany('''
        INSERT INTO pegel_{0} (messstelle_nr, zeit, {0}, {1}, {2})
        VALUES (?, ?, ?, ?, ?)
    '''.format(art, min_wert, max_wert), data)
    connection.commit()

    values = [x[2] for x in data if x[2] is not None]
    mean = sum(values) / len(values) if values else None
    max_value = max(x[4] for x in data if x[4] is not None)
    min_value = min(x[3] for x in data if x[3] is not None)

    print(';'.join(map(str, [data[0][0], art, round(mean, 3), max_value, min_value])))

    return sum(values), len(values), max_value, min_value, art


def read_meta_data(path, connection, cursor):
    """
    Reads metadata from an Excel file, and inserts it into the 'pegel_meta' table in the database.

    Args:
        path (str): The path to the Excel file containing the metadata.
        connection: A connection object to the database.
        cursor: A cursor object for executing SQL commands.
    """
    data = pd.read_excel(path)
    data = data.where(pd.notnull(data), None)

    cursor.executemany('''
        INSERT INTO pegel_meta (MesstellenNr, Standort, Gewaesser, Einzugsgebiet_Oberirdisch, Status, 
        Entfernung_Muendung, Messnetz_Kurzname, Ostwert, Nordwert, MB, MS1, MS2, MS3)
        VALUES (?,''' + ','.join(['?'] * 12) + ')', data.values)
    cursor.execute("ALTER TABLE pegel_meta RENAME COLUMN MesstellenNr TO messstelle_nr")
    connection.commit()


conn = sqlite3.connect(db_path)
curs = conn.cursor()
create_tables(conn, curs)
clear_tabels(conn, curs)

q_files = [file for file in data_path.iterdir() if 'q' in file.name]
w_files = [file for file in data_path.iterdir() if 'w' in file.name]

for file in q_files:
    try:
        read_calc(file, 'q', conn, curs)
    except Exception as e:
        print(f"Error processing {file}: {e}")

for file in w_files:
    try:
        read_calc(file, 'w', conn, curs)
    except Exception as e:
        print(f"Error processing {file}: {e}")

read_meta_data(meta_data_path, conn, curs)
conn.close()

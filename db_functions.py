import os
import sqlite3

database_dir = os.path.join(os.getcwd(), '.dbs')
app_database = os.path.join(database_dir, 'app_db.db')

# # Creeate the directory if not exists
# if not os.path.exists(database_dir):
#     os.makedirs(database_dir, exist_ok=True)
# open(app_database, 'a').close()

# Create the table in database
def create_database_or_database_table(table_name: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (song TEXT)""")
    connection.commit()
    connection.close()


def add_song_to_database_table(song: str, table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()

    try:
        cursor.execute(f"""INSERT INTO {table} (song) VALUES (?)""", (song,))
        connection.commit()
        print(f"Successfully added: {song} to {table}")
        cursor.execute(f"SELECT * FROM {table}")
        results = cursor.fetchall()
        print("Current favorites:", results)
    except Exception as e:
        print(f"Error adding song to {table}: {e}")
    finally:
        connection.close()

# DELETE all songs from a database table
def delete_all_songs_from_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""DELETE FROM {table}""")
    connection.commit()
    connection.close()

# FETCH all songs from a database table
def fetch_all_songs_from_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""SELECT song FROM {table}""")
    song_data = cursor.fetchall()
    data = [song[0] for song in song_data]
    connection.commit()
    connection.close()

    return data

# Get all tables in the database
def get_playlist_tables():
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute("""SELECT * from sqlite_master WHERE type = 'table';""")
        table_names = cursor.fetchall()
        tables = [table_name[1] for table_name in table_names]

        return tables
    except sqlite3.Error as e:
        print(f"Error getting table names: {e}")
    finally:
        connection.close()


# Delete database table
def delete_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""DROP TABLE {table}""")
    connection.commit()
    connection.close()


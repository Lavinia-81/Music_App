import os
import sqlite3


database_dir = os.path.abspath(os.path.join(os.getcwd(), ".dbs"))
app_database = os.path.join(database_dir, "app_db.db")

if not os.path.exists(database_dir):
    print(f"Creating database directory at: {database_dir}")
    os.makedirs(database_dir)

if not os.path.exists(app_database):
    print(f"Creating new database file at: {app_database}")
else:
    print(f"Database file already exists at: {app_database}")



# Create the table in database
def create_database_or_database_table(table_name: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (song TEXT)""")
    connection.commit()
    connection.close()



# INSERT SONGS INTO TABLE
def add_song_to_database_table(song: str, table: str, database=app_database):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    query = f"""INSERT INTO "{table}" (song) VALUES (?)"""
    cursor.execute(query, (song,))
    connection.commit()
    connection.close()



# DELETE SONGS FROM DATABASE
def delete_song_from_database_table(song: str, table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT song, COUNT(*) FROM favourites GROUP BY song HAVING COUNT(*) > 1;")
        duplicates = cursor.fetchall()
        cursor.execute(f"DELETE FROM {table} WHERE song = ?", (song,))
        connection.commit()
        print("Song deleted successfully")
        cursor.execute(f"SELECT * FROM {table}")
        results = cursor.fetchall()
        print("Remaining songs in favourites:", results)
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM favourites")
        results = cursor.fetchall()
        connection.close()
        print("Remaining songs after deletion:", results)
    except Exception as e:
        print(f"Error deleting song from {table}: {e}")

    finally:
        connection.close()



# DELETE ALL THE SONGS FROM DATABASE
def delete_all_songs_from_database_table(table: str):
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM {table}")
        connection.commit()
        print("All songs deleted successfully!")  # Debugging
    except Exception as e:
        print(f" Error deleting all songs from {table}: {e}")
    finally:
        connection.close()



# FETCH ALL SONGS FROM DATABASE
def fetch_all_songs_from_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"SELECT song FROM {table}")
    song_data = cursor.fetchall()
    connection.close()
    print(f"Songs from {table}:", song_data)
    return [song[0] for song in song_data]



# GET ALL TABLE IN THE DATABASE
def get_playlist_tables():
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        table_names = cursor.fetchall()
        print(f"DEBUG: Retrieved raw playlist names = {table_names}")
        tables = [table_name[0] for table_name in table_names]
        return tables
    except sqlite3.Error as e:
        print(f"Error getting playlist names: {e}")
    finally:

        connection.close()



# DELETE DATABASE TABLE
def delete_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""DROP TABLE {table}""")
    connection.commit()
    connection.close()

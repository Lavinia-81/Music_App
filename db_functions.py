import os
import sqlite3


database_dir = os.path.abspath(os.path.join(os.getcwd(), ".dbs"))
app_database = os.path.join(database_dir, "app_db.db")

if not os.path.exists(database_dir):
    print(f"Creating database directory at: {database_dir}")
    os.makedirs(database_dir)

# if not os.path.exists(app_database):
#     print(f"Creating new database file at: {app_database}")
# else:
#     print(f"Database file already exists at: {app_database}")



# Create the table in database
def create_database_or_database_table(table_name: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    # Create a table with a single column 'song' if it does not exist
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (song TEXT)""")
    connection.commit()
    connection.close()



# Function to insert a song into the specified table
def add_song_to_database_table(song: str, table: str, database=app_database):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    # Insert the song into the table
    cursor.execute(f"""INSERT INTO "{table}" (song) VALUES (?)""", (song,))
    connection.commit()
    connection.close()



# Function to delete a specific song from the database table
def delete_song_from_database_table(song: str, table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    # Delete the first occurrence of the song based on its ROWID
    cursor.execute(
        f"""DELETE FROM {table} WHERE
         ROWID = (SELECT MIN(ROWID) FROM favourites 
         WHERE song = "{song}");""")

    connection.commit()
    connection.close()


# Function to delete all songs from the specified table
def delete_all_songs_from_database_table(table: str):
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        # Delete all rows from the table
        cursor.execute(f"DELETE FROM {table}")
        connection.commit()
    except Exception as e:
        print(f" Error deleting all songs from {table}: {e}")
    finally:
        connection.close()




# Function to fetch all songs from the specified table
def fetch_all_songs_from_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    # Retrieve all song names from the table
    cursor.execute(f"SELECT song FROM {table}")
    song_data = cursor.fetchall()
    connection.close()
    # print(f"Songs from {table}:", song_data)
    return [song[0] for song in song_data]



# Function to get all table names in the database
def get_playlist_tables():
    try:
        connection = sqlite3.connect(app_database)
        cursor = connection.cursor()
        # Retrieve the names of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        table_names = cursor.fetchall()
        # print(f"DEBUG: Retrieved raw playlist names = {table_names}")
        tables = [table_name[0] for table_name in table_names] # Extract table names
        return tables
    except sqlite3.Error as e:
        print(f"Error getting playlist names: {e}")
    finally:

        connection.close()



# Function to delete an entire database table
def delete_database_table(table: str):
    connection = sqlite3.connect(app_database)
    cursor = connection.cursor()
    cursor.execute(f"""DROP TABLE {table}""") # Drop the table from the database
    connection.commit()
    connection.close()

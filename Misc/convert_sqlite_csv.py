import pandas as pd
import sqlite3
# Paths
csv_file_path = "C:/Users/Ryan/Desktop/NBA_Basic1.csv"
sqlite_file_path = 'C:/Users/Ryan/Desktop/NBA_AI_Model/Data/dataset.sqlite'  # Adjust if necessary

# Read CSV into DataFrame
df = pd.read_csv(csv_file_path, low_memory=False)

# Connect to SQLite database
con = sqlite3.connect(sqlite_file_path)

# Replace existing table with DataFrame content
table_name = 'nba_dataset'  # Confirm table name
df.to_sql(table_name, con, if_exists='replace', index=False)

# Close the connection
con.close()

# Specify your SQLite database file path
# db_path = 'C:/Users/Ryan/Desktop/NBA_AI_MODEL/Data/dataset.sqlite'

# # Specify the table you want to export to CSV
# table_name = 'nba_dataset'

# # Specify the path for the resulting CSV file
# csv_file_path = 'C:/Users/Ryan/Desktop/NBA_Basic1.csv'

# # Connect to the SQLite database
# conn = sqlite3.connect(db_path)

# '''cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = [row[0] for row in cursor.fetchall()]
# print(tables)'''


# # Read the table into a pandas DataFrame
# df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
# #df = df[df['Year'] == 2024]

# # Close the connection to the database
# conn.close()

# # Write the DataFrame to a CSV file
# df.to_csv(csv_file_path, index=False)

import os
from datetime import datetime
 
from utils.config import FOLDER_LIVE_DATA

def get_most_recent_csv(folder_path, prefix):
    try:
        files = []
        # Get a list of all CSV files in the folder
        for file in os.listdir(folder_path):
            if file.startswith(prefix) and file.endswith(".csv"):
                    files.append(file)

        # Sort the scraped CSV files based on the timestamp in their names
        files.sort(key=lambda x: datetime.strptime(x.split("_")[2].split(".")[0], "%Y%m%d%H%M"))
        # Get the most recent scraped CSV file
        most_recent_file = str(files[-1]) if files else None
        # Return the names of the most recent CSV files for both categories as strings
        return most_recent_file
    except (OSError, IOError) as e:
        print("Error occurred while accessing the folder:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None
    
# The most up to date scrapped csv version
LIVE_SCRAPPED_TABLE = get_most_recent_csv(folder_path=f'{FOLDER_LIVE_DATA}', prefix="scrapped")
LIVE_PROCESSED_TABLE = get_most_recent_csv(folder_path=f'{FOLDER_LIVE_DATA}', prefix="processed")




# Once we get the most up to date we rename it
# Should we delete the all the other csv once the database is created ?
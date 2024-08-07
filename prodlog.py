import json
from datetime import datetime
from timer import notify

log_file_path = '/usr/share/prodlog/log.json'

# Update JSON log with new entry
def log_pomodoro(pomodoro_time, category, date):
    
    # Initialize log as an empty list if the file doesn't exist
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as file:
            json.dump([], file)

    with open(log_file_path, 'r+') as file:
        log = json.load(file)
        entry = {'date': date, 'length': pomodoro_time, 'category': category}
        log.append(entry)
        file.seek(0)  # Move file pointer to the beginning of the file
        json.dump(log, file, indent=4)
        file.truncate()  # Remove any remaining bytes

# Query JSON log
def query_log(category, date_str):
    with open(log_file_path, 'r') as file:
        log = json.load(file)
    
    total_time = 0
    target_date = datetime.strptime(date_str, '%Y-%m-%d_%H:%M:%S')
    
    for entry in log:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d_%H:%M:%S')
        
        # User might query for year, month, or precise day
        if target_date.year == entry_date.year:
            if target_date.month == entry_date.month or target_date.month is None:
                if target_date.day == entry_date.day or target_date.day is None:
                    if category in entry:
                        total_time += entry[category].get('length', 0)
    
    if total_time == 0:
        notify("No entries found for category '{category}' on date '{date_str}'.") # this needs to be updated to work with the notify function
    
    return total_time

if __name__ == '__main__':
    main()


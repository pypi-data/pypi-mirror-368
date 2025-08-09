'''
step 1: Add 'from track_exception import error_log, raiseWebSiteExceptions, setup_exception' line in every script
step 2: Add 'local_ip, script_path, track_url = setup_exception(url)' line after import library code block and pass main url to this function.
step 3: Add raiseWebSiteExceptions code block after driver.get(url)
step 4: add path of script in target_file variable Run replace code script after and run
'''

class PageNotFound(Exception):
    """Raised when page not found"""
    pass

class WebServerError(Exception):
    """Raised when there is 404 error on website"""
    pass

class SiteNotReached(Exception):
    """Raised when site can’t be reached"""
    pass

def raiseWebSiteExceptions(driver):
    page_source = str(driver.page_source).lower()
    if '404 error' in page_source or '404 not found' in page_source:
        raise WebServerError("404 Error On Website.")
    
    if 'page not found' in page_source: 
        raise PageNotFound("Page Not Found")
    
    if 'this site can’t be reached' in page_source:
        raise SiteNotReached("this site can’t be reached")
    
def connect_db():
    import sqlite3    
    import os
    
    db_path = os.path.expanduser('~') + "\\Documents\\Track_Exceptions\\Track_Exceptions.db"

    try:
        conn = sqlite3.connect(db_path, timeout=30)
        conn.execute('PRAGMA journal_mode=WAL;')
        
        # Use context to ensure cursor closes cleanly
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_log (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    SYSTEM_IP TEXT,
                    SCRIPT_NAME TEXT,
                    EXCEPTION_CLASS TEXT,
                    TRACEBACK_DETAILS TEXT,
                    URL TEXT,
                    CreatedOn TEXT DEFAULT (DATETIME('now', 'localtime'))
                )
            """)

        return conn
    except sqlite3.Error as e:
        print(f"[DB Error] Failed to connect or initialize DB: {e}")
        raise
    
def setup_exception(url):
    import socket
    import os
    import inspect

    """
    Prepares context information for error logging:
    - Gets the caller script's path
    - Gets the local IP and hostname
    - Stores the provided URL
    """
    # Attempt DB connection (for testing/logging setup)
    # conn = connect_db()
    # conn.close()

    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "No IP Found."  # fallback

    # Get the script path of the caller
    caller_frame = inspect.stack()[1]
    caller_path = os.path.abspath(caller_frame.filename)

    return local_ip, caller_path, url

def error_log(e, local_ip, script_path, URL):
    import traceback
    import sqlite3
    import time
    
    EXCEPTION_CLASS = type(e).__name__
    TRACEBACK_DETAILS = traceback.format_exc()
    
    max_retries = 5
    wait_seconds = 2
    
    for attempt in range(1, max_retries + 1):
        try:  
            with connect_db() as conn:
                conn.execute("""
                    INSERT INTO error_log (SYSTEM_IP, SCRIPT_NAME, EXCEPTION_CLASS, TRACEBACK_DETAILS, URL) 
                    VALUES (?, ?, ?, ?, ?)
                """, (local_ip, script_path, EXCEPTION_CLASS, TRACEBACK_DETAILS, URL))
                conn.commit()
            print(f"[✔] Error logged successfully on attempt {attempt}")
            break
        except sqlite3.OperationalError as db_err:
            if 'locked' in str(db_err).lower():
                print(f"[!] Database is locked. Retry {attempt}/{max_retries} in {wait_seconds} seconds...")
                time.sleep(wait_seconds)
                continue
            else:
                print(f"[✖] SQLite OperationalError: {db_err}")
                break  # not a lock issue, don't retry
        except Exception as unexpected_err:
            print(f"[‼] Unexpected error while logging exception: {unexpected_err}")
            break  # something else went wrong
    else:
        print("[×] Failed to log error after multiple attempts.")
        print("Fallback log:")
        print("IP:", local_ip)
        print("Script:", script_path)
        print("Exception:", EXCEPTION_CLASS)
        print("Traceback:", TRACEBACK_DETAILS)
        print("URL:", URL)
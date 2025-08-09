'''
step 1: Add 'from track_exception import error_log, raiseWebSiteExceptions, setup_exception' line in every script
step 2: Add 'local_ip, script_path, track_url = setup_exception(url)' line after import library code block and pass main url to this function.
step 3: Add raiseWebSiteExceptions code block after driver.get(url)
step 4: add path of script in target_file variable Run replace code script after and run
'''
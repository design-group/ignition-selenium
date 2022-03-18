from perspective_automation.selenium import Session, Credentials
import time, sys, linecache

def getException():
	"""
	If you put this in a generic try...except block that continues to raise the error, you can cleanly get a defined error message in the logs, without changing applciation logic.
	
	Example Error: 
		(<module:MES.Workorder>, LINE 270 ""): sequence item 0: expected string, NoneType found
	
	Example Use:
		try:
			# Execute code here	
			
		except Exception as e:
			logger.error(General.Errors.getException())
			raise(e)
	"""
	exc_type, exc_obj, tb = sys.exc_info()
			
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	return '{}({}, LINE {} "{}"): {}'.format(exc_type.__name__, filename, lineno, line.strip(), exc_obj)


if __name__ == '__main__':
    credentials = Credentials('RATester01', "N3verp@tch2021")
    
    try:
        with Session(base_url="http://localhost", page_path="/", wait_timeout_in_seconds=60, credentials=credentials, headless=False) as session:
            time.sleep(10)
    except Exception as e:
        print(getException())
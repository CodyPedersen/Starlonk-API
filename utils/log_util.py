from functools import wraps
from datetime import datetime

def log_data(data, date=True, stdout=True):
    with open("log.txt", mode="a+") as logfile:
        date_log = ''
        if date:
            date_log = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': '
        try:
            logfile.write(date_log + data + "\n")
            if stdout:
                print(date_log + data + "\n")
        except:
            logfile.write("Failed to write to log file\n")

# def log(f):
#     @wraps(f)
#     async def wrapper(*args, **kwargs):
#         args_repr = [repr(a) for a in args]
#         kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
#         all_args = ", ".join(args_repr + kwargs_repr)
#         log_data(f"Executing {f.__name__}({all_args})")
#         try:
#             return await f(*args, **kwargs)
#         except Exception as e:
#             log_data(f"Exception raised in {f.__name__}. exception: {str(e)}")
#             raise e
#     return wrapper
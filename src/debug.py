
from datetime import datetime


DEBUGLEVEL = 1

def debug(output):
    if DEBUGLEVEL > 0:
        currDateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{currDateTime}] {output}")
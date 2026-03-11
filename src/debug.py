
"""Simple debug logging helper."""

from datetime import datetime


DEBUGLEVEL = 1

def debug(output):
    """Prints a timestamped debug message when DEBUGLEVEL > 0."""
    if DEBUGLEVEL > 0:
        currDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{currDateTime}] {output}")
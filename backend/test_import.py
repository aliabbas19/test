import traceback
import sys
try:
    from app.main import app
    print("Imported app.main successfully")
except Exception:
    with open("traceback_error.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Error written to traceback_error.txt")

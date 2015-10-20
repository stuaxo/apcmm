import traceback
import sys

def main():
    try:
        from main import main as emumain
        emumain()
    except Exception as e:
        print e
        #traceback.print_exc(file=sys.stdout)
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)


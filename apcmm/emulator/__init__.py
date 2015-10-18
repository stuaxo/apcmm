def main():
    try:
        from emulator import main as emumain
        emumain()
    except Exception as e:
        print e


from database.db_manager import create_table
from gui.home_screen import HomeScreen


def main():

    create_table()

    app = HomeScreen()

    app.mainloop()


if __name__ == "__main__":
    main()
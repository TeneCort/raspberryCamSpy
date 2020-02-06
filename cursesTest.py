import curses

cur = curses.initscr()

try:
    while True:
        char = cur.getch()
        if char > 0:
             print(chr(char) + "\r")
except KeyboardInterrupt:
    print("Done")

curses.endwin()
print("BB")

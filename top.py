import random, curses, os, sys, time, re, psutil

def main():
    curses.wrapper(trash)
    curses.endwin()

def temp(stdscr):
    # TERM=xterm-256color !!!!!!!!!!!!!!!!!REQUIRED!!!!!!!!!!!!!!!!!
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    try:
        for i in range(0, 255):
            stdscr.addstr(str(i), curses.color_pair(i))
    except curses.ERR:
        # End of screen reached
        pass
    stdscr.getch()

def normalize(num):
    # this needs to take in 3500 and convert it into a length that will fit in
    # (curses.COLS // 2)  
    return num + 1

def trash(stdscr):
    k = 0
    cpus = []
    curses.initscr()
    curses.noecho()
    curses.cbreak()

    # delays getch() by 10 tenths of a second
    curses.halfdelay(10)

    # init colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors() # allows for more colors
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        try:
            curses.init_pair(6, 240, -1)
        except:
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)

    top_window_cols = (psutil.cpu_count() // 2)+ 4

    # TODO: curses.KEY_RESIZE() for window resizing

    while k != ord('q'):

        top_window = curses.newwin(top_window_cols, curses.COLS, 0, 0)
        bottom_window = curses.newwin(curses.LINES - top_window_cols, curses.COLS, top_window_cols, 0)

        max_num_cols = (curses.COLS // 2) - 10 # len('1[ 95.6%] ')

        left = True
        for i, percent in enumerate(psutil.cpu_percent(percpu = True)):

            # Left bar
            if left:
                top_window.addstr(i, 0, str(i + 1), curses.color_pair(5))
                top_window.addstr(i, 1, '[')
                top_window.attron(curses.color_pair(4))
                top_window.addstr('|' * round((percent / 100) * max_num_cols))
                top_window.attroff(curses.color_pair(4))
                top_window.addstr(i, max_num_cols + 3, str(percent) + '%', curses.color_pair(6))
                top_window.addstr(']')
                left = False
            else:
                # Right bar
                top_window.addstr(i - 1, curses.COLS // 2, str(i + 1), curses.color_pair(5))
                top_window.addstr(i - 1, curses.COLS // 2 + 1, '[')
                top_window.attron(curses.color_pair(4))
                top_window.addstr('|' * round((percent / 100) * max_num_cols))
                top_window.attroff(curses.color_pair(4))
                top_window.addstr(i - 1, (curses.COLS // 2) + max_num_cols, str(percent) + '%', curses.color_pair(6))
                top_window.addstr(']')
                left = True 
        
        top_window.addstr(top_window_cols- 1, 0, 'CPU [')
        cpu_percent = psutil.cpu_percent()
        top_window.attron(curses.color_pair(2))
        # top_window.addstr(top_window_cols - 1, len('CPU [') + 1, '|' * round(cpu_percent * max_num_cols))
        top_window.addstr('|' * round(cpu_percent / 100 * max_num_cols))
        top_window.attroff(curses.color_pair(2))
        top_window.addstr(top_window_cols - 1, max_num_cols + 3, str(cpu_percent) + '%', curses.color_pair(6))
        top_window.addstr(']')

        top_window.addstr(top_window_cols - 1, curses.COLS // 2, 'UPTIME ')
        top_window.attron(curses.color_pair(2))
        top_window.addstr(top_window_cols - 1, (curses.COLS // 2) + len('UPTIME '), str(round((time.time() - psutil.boot_time()) / 3600, 2)) + ' hours')
        top_window.attroff(curses.color_pair(2))

        top_window.noutrefresh()

        statusbar = ' PID    MEM     CPU     NAME '

        bottom_window.attron(curses.color_pair(1))
        bottom_window.addstr(0, 0, statusbar)
        bottom_window.addstr(0, len(statusbar), " " * (curses.COLS - len(statusbar)))
        bottom_window.attroff(curses.color_pair(1))

        for i, proc in enumerate(psutil.process_iter()):
            mem_percent = str(round(proc.memory_percent(), 2))
            bottom_window.addstr(i + 1, 0, 'MEM%  ' + mem_percent)

            cpu_percent = str(round(proc.cpu_percent(), 2))
            bottom_window.addstr(i + 1, len('MEM% ' + mem_percent) + 2, 'CPU% ' + cpu_percent)
            
            name = str(proc.name())
            bottom_window.addstr(i + 1, len('CPU%' + cpu_percent + 'MEM%  ' + mem_percent) + 9, 'NAME ' + name)

        bottom_window.noutrefresh()

        curses.doupdate()
        
        k = bottom_window.getch()

if __name__ == "__main__":
    main()
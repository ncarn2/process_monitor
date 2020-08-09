from typing import List
import time
from signal import signal, SIGWINCH
import sys
import argparse
import curses 
import psutil
import threading

class Screen():
    __version__ = 0.1
    __author__ = 'Nicholas Carnival'

    def __init__(self, menu='process_monitor'):
        self.menu = menu
        self.options = [ord('q'), ord('G'), ord('h'), ord('s'), ord('j'), ord('k')]
        self.process_list: List[psutil.Process]
        self.sorted_by = 'PID'
        self.sort_processes()
        self.cursor_position = 0
        self.k = 0 # user input variable

    def init_curses(self):
        self.max_y, self.max_x = curses.initscr().getmaxyx()
        # make cursor invisible
        curses.curs_set(0)
        curses.noecho()

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

    def resize_handler(self, signum, frame):
        self.max_y, temp = self.top_window.getmaxyx()
        self.top_window.clear()
        self.bottom_window.clear()
        self.last_updated = -1
        self.create_windows()

    def create_windows(self):
        self.top_window_rows = (psutil.cpu_count() // 2) + 4

        self.top_window = curses.newwin(self.top_window_rows, self.max_x, 0, 0)
        # TODO: this should be a pad. It can be larger than the display size :)
        self.bottom_window = curses.newpad(100, self.max_x)
        self.bottom_window_depth = curses.LINES - self.top_window_rows

        self.top_window.timeout(1000)
        self.bottom_window.timeout(1000)

    def start(self):
        signal(SIGWINCH, self.resize_handler)
        self.create_windows()
        self.last_updated = -1 # -1 to start
        curses.wrapper(self.main_loop)

    def stop(self):
        curses.endwin()

    def main_loop(self, stdscr):
        if self.k == curses.KEY_RESIZE:
            self.create_windows()
            self.stop()
            print("SHIT", curses.KEY_RESIZE)

        while True:
            if self.k in self.options:
                if self.k == ord('q'):
                    return
                elif self.k == ord('h'):
                    self.help_menu(stdscr)
                    self.last_updated = -1 # Allow the top_window to update immediately after leaving help menu
                elif self.k == ord('s'):
                    self.setup_menu(stdscr)
                    self.last_updated = -1 # Allow the top_window to update immediately after leaving help menu
                elif self.k == ord('G'):
                    self.cursor_position = self.bottom_window_depth - 2
                elif self.k == ord('k'):
                    # up
                    if self.cursor_position == 0: self.cursor_position = len(self.process_list) - 1
                    else: self.cursor_position -= 1
                elif self.k == ord('j'):
                    # down
                    if self.cursor_position == len(self.process_list) - 1:
                        self.cursor_position = 0
                    else: self.cursor_position += 1

            if self.cursor_position >= len(self.process_list):
                self.cursor_position = 0 

            self.system_monitor()

            self.sort_processes()
            self.process_monitor()

            if time.time() - self.last_updated > 1.0 or self.last_updated == -1: # this seems like a terrible way to do this :(
                self.last_updated = time.time()
                self.top_window.refresh() # TODO: refresh thitime.time() - self.start_time > 1.0s one every second no matter what !!
            self.bottom_window.refresh(0, 0, self.top_window_rows + 1, 0, curses.LINES - 2, self.max_x - 2)

            self.k = self.bottom_window.getch() # Get the users input

        self.stop()

    def help_menu(self, stdscr):
        """
        Display the usage stuff
        """
        stdscr.clear()

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr('system_monitor' + str(self.__version__) + ' - (C) 2020 ' + self.__author__)
        stdscr.addstr('\nReleased under the GNU GPL.')
        stdscr.attroff(curses.color_pair(4))

        stdscr.addstr('\nCPU usage bar: []')
        stdscr.addstr('\nMemory bar: []')
        stdscr.addstr('\nSwap bar: []')
        stdscr.addstr('\nType and layout of header meters are configurable in the setup screen')
        stdscr.addstr('\n\tStatus ')
        stdscr.addstr('\nPress any key to return...', curses.color_pair(3))

        stdscr.refresh()
        self.k = stdscr.getch()
        stdscr.clear()
        stdscr.refresh()

    def setup_menu(self, stdscr):
        """
        Display the setup stuff
        """
        stdscr.clear()

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr('\nReleased under the GNU GPL.')
        stdscr.attroff(curses.color_pair(4))
        stdscr.addstr('SETUP SCREEN', curses.color_pair(3))
        stdscr
        stdscr.addstr('\nPress any key to return...', curses.color_pair(3))

        stdscr.refresh()
        self.k = stdscr.getch()
        stdscr.clear()
        stdscr.refresh()
            
    def system_monitor(self):
        # We just need to update one thing from here ...
        self.top_window.erase()
        max_num_cols = (self.max_x // 2) - len('1[ 100.0%] ')
        cpu_num = 0

        cpu_percents = psutil.cpu_percent(percpu = True)
        # Display the Current CPU Usage Stats
        for i in range(len(cpu_percents) // 2):

            # Left bar
            percent = cpu_percents[cpu_num]
            cpu_num += 1
            self.top_window.addstr(i, 0, str(cpu_num), curses.color_pair(5))
            self.top_window.addstr(i, 1, '  [')
            self.top_window.attron(curses.color_pair(4))
            # self.top_window.addstr('|' * round((percent / 100) * max_num_cols))
            self.top_window.addstr('|' * round((percent/  100) * max_num_cols))
            self.top_window.attroff(curses.color_pair(4))
            self.top_window.addstr(i, max_num_cols + 3, str(percent) + '%', curses.color_pair(6))
            self.top_window.addstr(']')

            percent = cpu_percents[cpu_num]
            cpu_num += 1
            self.top_window.addstr(i, self.max_x // 2, str(cpu_num), curses.color_pair(5))
            self.top_window.addstr(i, self.max_x // 2 + 1, '[')
            self.top_window.attron(curses.color_pair(4))
            self.top_window.addstr('|' * round((percent / 100) * max_num_cols))
            self.top_window.attroff(curses.color_pair(4))
            self.top_window.addstr(i, (self.max_x // 2) + max_num_cols, str(percent) + '%', curses.color_pair(6))
            self.top_window.addstr(']')

        # Mem Usage
        mem_tot = round(psutil.virtual_memory().total  * 0.000000001, 1)
        mem_current = round(mem_tot - (psutil.virtual_memory().available * 0.000000001), 1) 

        self.top_window.addstr(self.top_window_rows - 4, 0, 'MEM[', curses.color_pair(5))        
        self.top_window.addstr(self.top_window_rows - 4, len('MEM'), '[')
        self.top_window.attron(curses.color_pair(4))
        self.top_window.addstr('|' * round((mem_current / mem_tot) * max_num_cols))
        self.top_window.attroff(curses.color_pair(4))
        self.top_window.addstr(self.top_window_rows - 4, max_num_cols - 1, str(mem_current) + '/' + str(mem_tot), curses.color_pair(6))
        self.top_window.addstr(']')

        # Swp Usage
        # swp_tot = round(psutil.swap_memory().total  * 0.000000001, 1)
        # swp_current = round(psutil.swap_memory().used * 0.000000001, 1)

        # self.top_window.addstr(self.top_window_rows - 3, 0, 'SWP[', curses.color_pair(5))        
        # self.top_window.addstr(self.top_window_rows - 3, len('SWP'), '[')
        # self.top_window.attron(curses.color_pair(4))
        # self.top_window.addstr('|' * round((swp_current / swp_tot) * max_num_cols))
        # self.top_window.attroff(curses.color_pair(4))
        # self.top_window.addstr(self.top_window_rows - 3, max_num_cols - 1, str(swp_current) + '/' + str(swp_tot), curses.color_pair(6))
        # self.top_window.addstr(']')

        # CPU Usage
        cpu_percent = psutil.cpu_percent()

        self.top_window.addstr(self.top_window_rows- 1, 0, 'CPU [')
        self.top_window.attron(curses.color_pair(2))
        self.top_window.addstr('|' * round(cpu_percent / 100 * max_num_cols))
        self.top_window.attroff(curses.color_pair(2))
        self.top_window.addstr(self.top_window_rows - 1, max_num_cols + 3, str(cpu_percent) + '%', curses.color_pair(6))
        self.top_window.addstr(']')

        c = time.time() - psutil.boot_time() 
        days = round(c // 86400)
        hours = round(c // 3600 % 24)
        minutes = round(c // 60 % 60)
        seconds = round(c % 60)

        self.top_window.addstr(self.top_window_rows - 1, self.max_x // 2, 'UPTIME ')
        self.top_window.attron(curses.color_pair(2))
        self.top_window.addstr(self.top_window_rows - 1, (self.max_x // 2) + len('UPTIME '), str(hours) + ":" + str(minutes) + ":" + str(seconds))
        self.top_window.attroff(curses.color_pair(2))

    def sort_processes(self):
        """
        Sorts the process_list based on self.sorted_by 
        - changes process_list rather than returning it
        """
        self.process_list = [x for x in psutil.process_iter()]

    def process_monitor(self):
        self.bottom_window.erase()

        # These should not be hard coded and should be dynamic
        pid_length = 5
        user_length = pid_length + 10
        mem_length = user_length + 6
        cpu_length = mem_length + 6
        name_length = cpu_length + 22

        self.bottom_window.attron(curses.color_pair(1))
        self.bottom_window.addstr(0, 0, 'PID' + ' ' * pid_length)
        self.bottom_window.addstr(0, pid_length, 'USER' + ' ' * user_length)
        self.bottom_window.addstr(0, user_length, 'MEM%' + ' ' * mem_length)
        self.bottom_window.addstr(0, mem_length, 'CPU%' + ' ' * cpu_length)
        self.bottom_window.addstr(0, cpu_length , 'Command' + ' ' * name_length)
            
        self.bottom_window.addstr(0, name_length, " " * (self.max_x - name_length))
        self.bottom_window.attroff(curses.color_pair(1))
        
        for i, proc in enumerate(self.process_list):
            if i >= self.bottom_window_depth - 2:
                break
            proc_name = ' '.join(proc.cmdline())
            if i == self.cursor_position and self.cursor_position < len(self.process_list):
                self.bottom_window.attron(curses.color_pair(2))
            else:
                self.bottom_window.attroff(curses.color_pair(2))

            self.bottom_window.addstr(i + 1, 0, str(proc.pid) + ' ' * pid_length)
            self.bottom_window.addstr(i + 1, pid_length, str(proc.username()) + ' ' * user_length)
            self.bottom_window.addstr(i + 1, user_length, str(round(proc.memory_percent(), 2)) + ' ' * mem_length)
            self.bottom_window.addstr(i + 1, mem_length, str(round(proc.cpu_percent(), 2)) + ' ' * cpu_length)
            self.bottom_window.addstr(i + 1, cpu_length, proc_name + ' ' * (self.max_x - cpu_length - len(proc_name)))


def init_args():
    parser = argparse.ArgumentParser(
        description = 'process monitor'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='Display version and exit'
    )

    args = vars(parser.parse_args())
    return args

def main():
    """
    handles args and starts the screen
    """

    args = init_args()

    temp = 'process_monitor'
    screen = Screen(menu=temp) #TODO: add an arg parser and pass into screen

    if args['version']:
        print('system_monitor v{}'.format(screen.__version__))
        sys.exit()

    screen.init_curses()
    screen.start()

if __name__ == "__main__":
    main()

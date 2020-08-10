from typing import List
import time

try:
    from signal import SIGWINCH
except ImportError:
    pass

import sys
import os
import argparse
import curses 
import psutil
from psutil import AccessDenied
from psutil import NoSuchProcess
import threading

class Screen():
    __version__ = 0.1
    __author__ = 'Nicholas Carnival'

    def __init__(self):
        # This is redundant, use self.keys eventually
        self.options = [ord('q'), ord('G'), ord('h'), ord('s'), ord('j'), ord('k')]
        self.process_list: List[psutil.Process]
        if os.name == 'nt':
            self.sorted_by = 'USER'
        else:
            self.sorted_by = 'PID'
        self.selecting_sort = False
        self.sort_processes()
        self.cursor_position = 0
        self.k = 0 # user input variable
        # TODO: use this to change keybindings...
        self.key_bindings = {'q': 'Quit', 'h': 'Help', 'k': 'Up', 'j': 'Down','s': 'Sort'}
        self.process_headers = [ ('PID', 6), ('USER', 15), ('MEM%', 6), ('CPU%', 6), ('Command', 22) ]

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
        # TODO: this is hardcoded the size should be based on how many processes there currently are, or something else
        self.bottom_window = curses.newpad(100, self.max_x)
        self.bottom_window_depth = curses.LINES - self.top_window_rows - 3 # idk why...

        self.top_window.timeout(1000)
        self.bottom_window.timeout(1000)

    def start(self):
        try: signal(SIGWINCH, self.resize_handler)
        except: pass
        self.create_windows()
        self.last_updated = -1 # -1 to start
        curses.wrapper(self.main_loop)

    def stop(self):
        curses.endwin()

    def sort_prompt(self):
        process_header_label = [x[0] for x in self.process_headers]
        current_sort_index = process_header_label.index(self.sorted_by)

        while self.selecting_sort: # until user has made a selection
            self.bottom_window.addstr(self.bottom_window_depth, 0, 'Select Sort: ', curses.color_pair(3))

            total_width = len('Select Sort: ')
            for header in self.process_headers: 
                if header[0] == self.sorted_by:
                    self.bottom_window.attron(curses.color_pair(2))
                else:
                    self.bottom_window.attron(curses.color_pair(1))
                self.bottom_window.addstr(self.bottom_window_depth, total_width, ' ' + header[0] + ' ')
                total_width += len(' ' + header[0] + ' ')

            self.bottom_window.refresh(0, 0, self.top_window_rows + 1, 0, curses.LINES - 2, self.max_x - 2)

            selection_input = self.bottom_window.getch()
            if selection_input == ord('q') or selection_input == ord('\n'):
                self.selecting_sort = False
            elif selection_input == ord('h'):
                if current_sort_index - 1 < 0: current_sort_index = 0
                else: current_sort_index -= 1
            elif selection_input == ord('l'):
                if current_sort_index + 1 >= len(process_header_label): current_sort_index = len(process_header_label) - 1
                else: current_sort_index += 1

            self.sorted_by = process_header_label[current_sort_index]

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
                    self.selecting_sort = True
                    self.sort_prompt()
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
                self.top_window.refresh() 
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

        stdscr.addstr('\nMost of the navigation in this application uses ')
        stdscr.addstr('vim', curses.color_pair(4))
        stdscr.addstr(' bindings: ')
        stdscr.addstr('H', curses.color_pair(4))
        stdscr.addstr(' up ')
        stdscr.addstr('J', curses.color_pair(4))
        stdscr.addstr(' down ')
        stdscr.addstr('K', curses.color_pair(4))
        stdscr.addstr(' left ')
        stdscr.addstr('L', curses.color_pair(4))
        stdscr.addstr(' right ')

        stdscr.addstr('\nCPU usage bar: []')
        stdscr.addstr('\nMemory bar: []')
        stdscr.addstr('\nSwap bar: []')
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
        if self.sorted_by == 'PID':
            self.process_list = [x for x in psutil.process_iter()]
        elif self.sorted_by == 'MEM%':
            # alphabetical
            self.process_list = []
        elif self.sorted_by == 'USER':
            # highest memory first
            self.process_list = []
            process_list = list(psutil.process_iter())
            something = {'' : [ ]}
            for proc in process_list:
                try:
                    if proc.username() not in something.keys():
                        something[proc.username()] = []
                    else:
                        something[proc.username()].append(proc)
                except (AccessDenied, NoSuchProcess) as e:
                    continue

            for l in something.values():
                for item in l:
                    self.process_list.append(item)
        elif self.sorted_by == 'CPU%':
            # highest cpu first
            # lets test with a bad algorithm...
            self.process_list = []
        elif self.sorted_by == 'Command':
            # similar users next toeach other
            alphabetical_dict = {'': []}
            for proc in list(psutil.process_iter()):
                try:
                    command = proc.cmdline()[0][0] # first character
                except AccessDenied:
                    continue
            for l in alphabetical_dict.values():
                for item in l:
                    self.process_list.append(item)

    def process_monitor(self):
        self.bottom_window.erase()

        # These should not be hard coded and should be dynamic
        pid_length = 6
        user_length = pid_length + 15
        mem_length = user_length + 6
        cpu_length = mem_length + 6
        command_length = cpu_length + 22

        total_width = 0
        for label in self.process_headers:
            if label[0] == self.sorted_by: 
                self.bottom_window.attron(curses.color_pair(2))
            else:
                self.bottom_window.attron(curses.color_pair(1))

            self.bottom_window.addstr(0, total_width , label[0])
            self.bottom_window.addstr(0, total_width + len(label[0]), ' ' * label[1])
            total_width += label[1]
            
        self.bottom_window.addstr(0, command_length, " " * (self.max_x - command_length))
        self.bottom_window.attroff(curses.color_pair(1))
        
        for i, proc in enumerate(self.process_list):
            if i >= self.bottom_window_depth:
                break
            try:
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
            except AccessDenied:
                i -= 1

        total_width = 0
        for key, value in self.key_bindings.items():
            self.bottom_window.addstr(self.bottom_window_depth, total_width, ' ' + str(key) + ' ', curses.color_pair(3) | curses.A_BOLD)
            total_width += len(str(key)) + 2
            self.bottom_window.addstr(self.bottom_window_depth, total_width, str(value), curses.color_pair(1))
            total_width += len(str(value))
        self.bottom_window.addstr(self.bottom_window_depth, total_width, ' ' * (curses.COLS), curses.color_pair(1))

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

    screen = Screen() 

    if args['version']:
        print('system_monitor v{}'.format(screen.__version__))
        sys.exit()

    screen.init_curses()
    screen.start()

if __name__ == "__main__":
    main()

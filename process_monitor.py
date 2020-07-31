from typing import List
import time
import sys
import random # TODO remove
import argparse
import curses, psutil

class Screen():
    """
    Beep Boop
    """
    __version__ = 0.1
    __author__ = 'Nicholas Carnival'

    def __init__(self, menu='process_monitor'):
        self.menu = menu
        self.options = [ord('q'), ord('h'), ord('s'), ord('j'), ord('k')]
        self.process_list: List[psutil.Process]
        self.sorted_by = 'PID'
        self.sort_processes()
        self.cursor_position = 0
        self.k = 0 # user input variable

    def start(self):
        curses.initscr()
        # make cursor invisible
        curses.curs_set(0)

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

        self.top_window_cols = (psutil.cpu_count() // 2) + 4

        self.top_window = curses.newwin(self.top_window_cols, curses.COLS, 0, 0)
        self.bottom_window = curses.newwin(curses.LINES - self.top_window_cols, curses.COLS, self.top_window_cols, 0)

        self.top_window.nodelay(True)
        self.bottom_window.nodelay(True)

        curses.wrapper(self.main_loop)

    def stop(self):
        curses.endwin()

    def help_menu(self, stdscr):
        """
        Display the usage stuff
        """
        stdscr.clear()
        stdscr.nodelay(False)

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr('top ' + str(self.__version__) + ' - (C) 2020 ' + self.__author__)
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
        stdscr.nodelay(True)
         

    def setup_menu(self, stdscr):
        """
        Display the setup stuff
        """
        stdscr.clear()
        stdscr.nodelay(False)

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr('\nReleased under the GNU GPL.')
        stdscr.attroff(curses.color_pair(4))
        stdscr.addstr('SETUP SCREEN', curses.color_pair(3))
        stdscr
        stdscr.addstr('\nPress any key to return...', curses.color_pair(3))

        stdscr.refresh()
        self.k = stdscr.getch()
        stdscr.nodelay(True)

    def main_loop(self, stdscr):
        # TODO: curses.KEY_RESIZE() for window resizing

        stdscr.nodelay(True)

        while True:
            if self.k in self.options:
                if self.k == ord('q'):
                    return
                elif self.k == ord('h'):
                    self.help_menu(stdscr)
                    self.top_window.clear()
                elif self.k == ord('s'):
                    self.setup_menu(stdscr)
                    self.top_window.clear()
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
            # refreshes process list
            self.sort_processes()
            self.process_monitor()

            self.top_window.refresh()
            self.bottom_window.refresh()

            time.sleep(1)
            self.k = stdscr.getch()

        self.stop()
            
    def system_monitor(self):
        max_num_cols = (curses.COLS // 2) - 10 # len('1[ 95.6%] ')

        cpu_percents = psutil.cpu_percent(percpu = True)
        cpu_num = 0

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
            self.top_window.addstr(i, curses.COLS // 2, str(cpu_num), curses.color_pair(5))
            self.top_window.addstr(i, curses.COLS // 2 + 1, '[')
            self.top_window.attron(curses.color_pair(4))
            self.top_window.addstr('|' * round((percent / 100) * max_num_cols))
            self.top_window.attroff(curses.color_pair(4))
            self.top_window.addstr(i, (curses.COLS // 2) + max_num_cols, str(percent) + '%', curses.color_pair(6))
            self.top_window.addstr(']')

        # Mem Usage
        mem_tot = round(psutil.virtual_memory().total  * 0.000000001, 1)
        mem_current = round(mem_tot - (psutil.virtual_memory().available * 0.000000001), 1) 

        self.top_window.addstr(self.top_window_cols - 4, 0, 'MEM[', curses.color_pair(5))        
        self.top_window.addstr(self.top_window_cols - 4, len('MEM'), '[')
        self.top_window.attron(curses.color_pair(4))
        self.top_window.addstr('|' * round((mem_current / mem_tot) * max_num_cols))
        self.top_window.attroff(curses.color_pair(4))
        self.top_window.addstr(self.top_window_cols - 4, max_num_cols - 1, str(mem_current) + '/' + str(mem_tot), curses.color_pair(6))
        self.top_window.addstr(']')

        # Swp Usage
        # swp_tot = round(psutil.swap_memory().total  * 0.000000001, 1)
        # swp_current = round(psutil.swap_memory().used * 0.000000001, 1)

        # self.top_window.addstr(self.top_window_cols - 3, 0, 'SWP[', curses.color_pair(5))        
        # self.top_window.addstr(self.top_window_cols - 3, len('SWP'), '[')
        # self.top_window.attron(curses.color_pair(4))
        # self.top_window.addstr('|' * round((swp_current / swp_tot) * max_num_cols))
        # self.top_window.attroff(curses.color_pair(4))
        # self.top_window.addstr(self.top_window_cols - 3, max_num_cols - 1, str(swp_current) + '/' + str(swp_tot), curses.color_pair(6))
        # self.top_window.addstr(']')

        # CPU Usage
        cpu_percent = psutil.cpu_percent()

        self.top_window.addstr(self.top_window_cols- 1, 0, 'CPU [')
        self.top_window.attron(curses.color_pair(2))
        self.top_window.addstr('|' * round(cpu_percent / 100 * max_num_cols))
        self.top_window.attroff(curses.color_pair(2))
        self.top_window.addstr(self.top_window_cols - 1, max_num_cols + 3, str(cpu_percent) + '%', curses.color_pair(6))
        self.top_window.addstr(']')

        self.top_window.addstr(self.top_window_cols - 1, curses.COLS // 2, 'UPTIME ')
        self.top_window.attron(curses.color_pair(2))
        self.top_window.addstr(self.top_window_cols - 1, (curses.COLS // 2) + len('UPTIME '), str(round((time.time() - psutil.boot_time()) / 3600, 2)) + ' hours')
        self.top_window.attroff(curses.color_pair(2))

    def sort_processes(self):
        """
        Sorts the process_list based on self.sorted_by 
        - changes process_list rather than returning it
        """
        self.process_list = [x for x in psutil.process_iter()]

    def process_monitor(self):
        self.bottom_window.clear()
        self.bottom_window.nodelay(True)


        # Display the status bar
        statusbar = ['PID', 'USER', 'MEM', 'CPU', 'NAME']
        total_length = 0
        for parameter in statusbar:
            if parameter == self.sorted_by:
                self.bottom_window.addstr(0, total_length, parameter + '    ', curses.color_pair(2))
            else:
                self.bottom_window.addstr(0, total_length, parameter + '    ', curses.color_pair(1))
            total_length += (len(parameter) + len('    '))
            
        self.bottom_window.addstr(0, total_length, " " * (curses.COLS - total_length), curses.color_pair(1))

        max_num_cols = (curses.COLS // 2) - 10 # len('1[ 95.6%] ')

        cpu_percents = psutil.cpu_percent(percpu = True)
        cpu_num = 0

        # TODO: keep track of which process the cursor is over, and display all processes
        # after the row the cursor is on below it up until the screen depth: 
        # (7 (however deep the top_window is)+ curses.ROWS). Highlight the row that the
        # cursor is over and accept new 'options'. Each screen should contain its own
        # options. Allow for sorting options, sort by PID, mem %, and cpu %. After a specific
        # key is pressed
        bottom_window_depth = curses.LINES - self.top_window_cols

        self.sort_processes()
        for i, proc in enumerate(self.process_list):
            mem_percent = str(round(proc.memory_percent(), 2))
            cpu_percent = str(round(proc.cpu_percent(), 2))
            name = str(proc.name())
            cleaned_process = str(proc.pid) + '    ' + mem_percent + '    ' + cpu_percent + '    ' + name + ' '

            if i == self.cursor_position and self.cursor_position < len(self.process_list):
                self.current_process = proc 

                self.bottom_window.attron(curses.color_pair(2))
                self.bottom_window.addstr(i + 1, 0, cleaned_process) 
                self.bottom_window.addstr(i + 1, len(cleaned_process),  ' ' * (curses.COLS- len(cleaned_process))) 
                self.bottom_window.attroff(curses.color_pair(2))
            else:
                self.bottom_window.addstr(i + 1, 0, cleaned_process) 
        self.bottom_window.addstr(bottom_window_depth - 1, 0, 'THE TEST OUTPUT: ' + str(self.current_process.pid) + ' ' + str(self.current_process.name()), curses.color_pair(3))

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
        print('process_monitor v{}'.format(screen.__version__))
        sys.exit()

    screen.start()

if __name__ == "__main__":
    main()

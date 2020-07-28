import time
import sys
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

        curses.initscr()
        # init refresh speed
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

    def start(self):
        stdscr = curses.initscr()

        if self.menu == 'process_monitor': curses.wrapper(self.process_monitor)
        elif self.menu == 'help': curses.wrapper(self.help_menu)
        elif self.menu == 'some_other_monitor': curses.wrapper(self.some_other_monitor)
        else: curses.wrapper(self.process_monitor)

        # help_menu(stdscr) # this is how ide like to do it

    def stop(self):
        curses.endwin()

    def help_menu(self, stdscr):
        """
        Display the usage stuff
        """
        stdscr.clear()

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
        k = stdscr.getch()

    def setup_menu(self, stdscr):
        """
        Display the usage stuff
        """
        stdscr.clear()

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
        k = stdscr.getch()

    def process_monitor(self, stdscr):
        stdscr.clear()
        top_window_cols = (psutil.cpu_count() // 2) + 4
        k = 0

        # TODO: curses.KEY_RESIZE() for window resizing

        args = [ord('q'), ord('h'), ord('s')]
        while k not in args:

            top_window = curses.newwin(top_window_cols, curses.COLS, 0, 0)
            bottom_window = curses.newwin(curses.LINES - top_window_cols, curses.COLS, top_window_cols, 0)

            max_num_cols = (curses.COLS // 2) - 10 # len('1[ 95.6%] ')

            cpu_percents = psutil.cpu_percent(percpu = True)
            cpu_num = 0

            # Display the Current CPU Usage Stats
            for i in range(len(cpu_percents) // 2):

                # Left bar
                percent = cpu_percents[cpu_num]
                cpu_num += 1
                top_window.addstr(i, 0, str(cpu_num), curses.color_pair(5))
                top_window.addstr(i, 1, '  [')
                top_window.attron(curses.color_pair(4))
                top_window.addstr('|' * round((percent / 100) * max_num_cols))
                top_window.attroff(curses.color_pair(4))
                top_window.addstr(i, max_num_cols + 3, str(percent) + '%', curses.color_pair(6))
                top_window.addstr(']')

                # Right bar
                percent = cpu_percents[cpu_num]
                cpu_num += 1
                top_window.addstr(i, curses.COLS // 2, str(cpu_num), curses.color_pair(5))
                top_window.addstr(i, curses.COLS // 2 + 1, '[')
                top_window.attron(curses.color_pair(4))
                top_window.addstr('|' * round((percent / 100) * max_num_cols))
                top_window.attroff(curses.color_pair(4))
                top_window.addstr(i, (curses.COLS // 2) + max_num_cols, str(percent) + '%', curses.color_pair(6))
                top_window.addstr(']')

                top_window.noutrefresh()
                bottom_window.noutrefresh()


            # Mem Usage
            mem_tot = round(psutil.virtual_memory().total  * 0.000000001, 1)
            mem_current = round(mem_tot - (psutil.virtual_memory().available * 0.000000001), 1) 

            top_window.addstr(top_window_cols - 4, 0, 'MEM[', curses.color_pair(5))        
            top_window.addstr(top_window_cols - 4, len('MEM'), '[')
            top_window.attron(curses.color_pair(4))
            top_window.addstr('|' * round((mem_current / mem_tot) * max_num_cols))
            top_window.attroff(curses.color_pair(4))
            top_window.addstr(top_window_cols - 4, max_num_cols - 1, str(mem_current) + '/' + str(mem_tot), curses.color_pair(6))
            top_window.addstr(']')

            # Swp Usage
            # swp_tot = round(psutil.swap_memory().total  * 0.000000001, 1)
            # swp_current = round(psutil.swap_memory().used * 0.000000001, 1)

            # top_window.addstr(top_window_cols - 3, 0, 'SWP[', curses.color_pair(5))        
            # top_window.addstr(top_window_cols - 3, len('SWP'), '[')
            # top_window.attron(curses.color_pair(4))
            # top_window.addstr('|' * round((swp_current / swp_tot) * max_num_cols))
            # top_window.attroff(curses.color_pair(4))
            # top_window.addstr(top_window_cols - 3, max_num_cols - 1, str(swp_current) + '/' + str(swp_tot), curses.color_pair(6))
            # top_window.addstr(']')

            # CPU Usage
            cpu_percent = psutil.cpu_percent()

            top_window.addstr(top_window_cols- 1, 0, 'CPU [')
            top_window.attron(curses.color_pair(2))
            top_window.addstr('|' * round(cpu_percent / 100 * max_num_cols))
            top_window.attroff(curses.color_pair(2))
            top_window.addstr(top_window_cols - 1, max_num_cols + 3, str(cpu_percent) + '%', curses.color_pair(6))
            top_window.addstr(']')

            top_window.addstr(top_window_cols - 1, curses.COLS // 2, 'UPTIME ')
            top_window.attron(curses.color_pair(2))
            top_window.addstr(top_window_cols - 1, (curses.COLS // 2) + len('UPTIME '), str(round((time.time() - psutil.boot_time()) / 3600, 2)) + ' hours')
            top_window.attroff(curses.color_pair(2))


            # Display the Current Processes
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

            top_window.noutrefresh()
            bottom_window.noutrefresh()

            curses.doupdate()
            
            time.sleep(1)

            k = top_window.getch()

        if k == ord('h'):
            curses.wrapper(self.help_menu(stdscr))
            curses.wrapper(self.process_monitor(stdscr)) #TODO: do this better! 
        elif k == ord('q'):
            self.stop()
        elif k == ord('s'):
            curses.wrapper(self.setup_menu(stdscr))
            curses.wrapper(self.process_monitor(stdscr)) #TODO: do this better! 
        else:
            self.stop()

def init_args():
    parser = argparse.ArgumentParser(
        description = 'process monitor'
    )
    parser.add_argument(
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
        print('top v{}'.format(screen.__version__))
        sys.exit()



    screen.start()

if __name__ == "__main__":
    main()
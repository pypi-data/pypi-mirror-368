import time
import sys
from datetime import datetime
from random import randint
from colorama import init, Fore, Back, Style

init()  # Initialize colorama

class ColorClock:
    def __init__(self, colored=True, military_time=False, show_date=False):
        """
        Initialize the colorful clock
        
        Args:
            colored (bool): Whether to use colors
            military_time (bool): 24-hour format if True
            show_date (bool): Show date if True
        """
        self.colored = colored
        self.military_time = military_time
        self.show_date = show_date
        self.running = False

    def _get_random_color(self):
        """Return a random color from colorama's Fore colors"""
        colors = [c for c in dir(Fore) if not c.startswith('_')]
        return getattr(Fore, colors[randint(0, len(colors)-1)])

    def display(self):
        """Display the continuously updating clock"""
        self.running = True
        try:
            while self.running:
                now = datetime.now()
                
                # Format time
                if self.military_time:
                    time_str = now.strftime("%H:%M:%S")
                else:
                    time_str = now.strftime("%I:%M:%S %p")
                
                # Add date if needed
                if self.show_date:
                    date_str = now.strftime("%Y-%m-%d ")
                    output = date_str + time_str
                else:
                    output = time_str
                
                # Add colors if enabled
                if self.colored:
                    color = self._get_random_color()
                    colored_output = f"{color}{output}{Style.RESET_ALL}"
                else:
                    colored_output = output
                
                # Print on the same line
                sys.stdout.write("\r" + colored_output)
                sys.stdout.flush()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()
            print("\nClock stopped.")

    def stop(self):
        """Stop the clock"""
        self.running = False
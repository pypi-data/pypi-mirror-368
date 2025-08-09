import unittest
from ASDFGH.clock import ColorClock
import time
from io import StringIO
import sys

class TestColorClock(unittest.TestCase):
    def setUp(self):
        self.clock = ColorClock(colored=False)
    
    def test_initialization(self):
        self.assertTrue(hasattr(self.clock, 'display'))
        self.assertTrue(hasattr(self.clock, 'stop'))
    
    def test_display_interrupt(self):
        import threading
        self.clock.running = True
        
        def stop_clock():
            time.sleep(1)
            self.clock.stop()
            
        threading.Thread(target=stop_clock).start()
        
        # Redirect stdout for testing
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            self.clock.display()
            output = out.getvalue()
            self.assertIn(":", output)  # Check if time format appears
        finally:
            sys.stdout = saved_stdout

if __name__ == '__main__':
    unittest.main()
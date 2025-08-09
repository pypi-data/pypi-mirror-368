#!/usr/bin/env python3
"""Hashing utility for generating unique IDs in base62 format."""
import time
from datetime import datetime
import pytz

class Generator:
    """Utility class for generating unique IDs in base62 format."""
    BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    counter = 0
    last_mill = None

    def __init__(self, timezone="UTC"):
        """Initialize the Generator."""
        self.timezone = pytz.timezone(timezone)


    def encode_base62(self, num):
        """Encodes a number into a base62 string."""
        base_chars = self.BASE62_CHARS

        if num == 0:
            return "0"
        base62 = ""
        while num > 0:
            num, rem = divmod(num, 62)
            base62 = base_chars[rem] + base62
        return base62
    
    def get_current_millis(self):
        """Get current timestamp in milliseconds (adjusted to timezone)."""
        dt = datetime.now(self.timezone)
        return int(dt.timestamp() * 1000)


    def generate(self):
        """Generates a unique ID based on the current time and a counter."""
        self.counter += 1
        if not self.last_mill:
            self.last_mill = self.get_current_millis()
        current_millis = self.get_current_millis()

        if current_millis != self.last_mill:
            self.counter = 0
            self.last_mill = current_millis          
        timestamp = int(time.time() * 1000)
        unique_number = timestamp * 1000 + self.counter 
        return self.encode_base62(unique_number)


if __name__ == "__main__":
    # Example usage
    hashing_util = Generator()
    unique_id = hashing_util.generate()
    print(f"Generated unique ID: {unique_id}")
    for i in range(5):
        print(hashing_util.generate())

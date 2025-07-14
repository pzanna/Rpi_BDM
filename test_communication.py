#!/usr/bin/env python3
"""
Simple test script to verify USB serial communication with RP2040
"""

import serial
import time
import sys

def test_communication(port):
    print(f"Testing communication with {port}")
    
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        print("Serial port opened successfully")
        
        # Wait a moment for any startup messages
        time.sleep(1)
        
        # Check if there's any data available
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"Received startup data: {data}")
        
        # Send a simple test command
        print("Sending test command...")
        ser.write(b"STATUS\n")
        
        # Wait for response
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"Response: '{response}'")
        else:
            print("No response received")
        
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_communication.py <serial_port>")
        print("Example: python test_communication.py /dev/cu.usbmodem2101")
        sys.exit(1)
    
    test_communication(sys.argv[1])

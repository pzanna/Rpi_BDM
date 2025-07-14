import serial
import time
import sys

class MC68332BDMHost:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        # Wait for device ready message (optional)
        self._wait_for_ready()

    def _wait_for_ready(self):
        """Wait for the RP2040 to signal readiness (with timeout)."""
        print("Waiting for RP2040 BDM interface...")
        start_time = time.time()
        timeout = 5  # 5 second timeout
        
        while time.time() - start_time < timeout:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    print(f"RP2040: {line}")
                    if "Ready" in line or "ready" in line.lower():
                        return
            time.sleep(0.1)
        
        print("No 'Ready' message received, but proceeding anyway...")
        print("You may need to load the BDM firmware on your RP2040.")

    def send_command(self, cmd):
        """Send command string and wait for single-line response."""
        cmd = cmd.strip()
        print(f">>> Sending: {cmd}")
        self.ser.write((cmd + '\n').encode('ascii'))
        resp = self.ser.readline().decode('ascii', errors='ignore').strip()
        print(f"<<< Response: {resp}")
        return resp

    def close(self):
        self.ser.close()

def usage():
    print("Usage: python mc68332_bdm_host.py <serial_port>")
    print("Example: python mc68332_bdm_host.py /dev/tty.usbmodem12345")

def interactive_shell(host):
    print("Enter commands (HELP for list). Ctrl+C to exit.")
    try:
        while True:
            cmd = input("BDM> ").strip()
            if not cmd:
                continue
            if cmd.upper() == "HELP":
                print(
                    "Commands:\n"
                    "  RESET            - Reset and run CPU\n"
                    "  STOP             - Halt CPU (enter BDM)\n"
                    "  GO               - Resume CPU from BDM\n"
                    "  READ_REG <reg>   - Read system register (hex)\n"
                    "  WRITE_REG <reg> <val> - Write register (hex)\n"
                    "  STATUS           - Get CPU status\n"
                    "  QUIT             - Exit program"
                )
                continue
            if cmd.upper() == "QUIT":
                break
            host.send_command(cmd)
    except KeyboardInterrupt:
        print("\nExiting...")

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    port = sys.argv[1]
    host = None

    try:
        host = MC68332BDMHost(port)
        interactive_shell(host)
    finally:
        if host:
            host.close()

if __name__ == "__main__":
    main()

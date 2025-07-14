import board
import digitalio
import time
import usb_cdc

usb_serial = usb_cdc.data
if usb_serial is None:
    usb_serial = usb_cdc.console

# Setup pins
dsclk = digitalio.DigitalInOut(board.GP15)
dsclk.direction = digitalio.Direction.OUTPUT
dsclk.value = True

dsi = digitalio.DigitalInOut(board.GP14)
dsi.direction = digitalio.Direction.OUTPUT
dsi.value = False

dso = digitalio.DigitalInOut(board.GP13)
dso.direction = digitalio.Direction.INPUT

freeze = digitalio.DigitalInOut(board.GP12)
freeze.direction = digitalio.Direction.INPUT

reset = digitalio.DigitalInOut(board.GP11)
reset.direction = digitalio.Direction.OUTPUT
reset.value = True

def bdm_transfer_word(cmd):
    response = 0
    for bit in range(16, -1, -1):
        out_bit = 0 if bit == 16 else (cmd >> bit) & 1
        dsi.value = bool(out_bit)
        time.sleep(0.00001)  # 10 us delay
        dsclk.value = False
        time.sleep(0.00001)
        dsclk.value = True
        in_bit = dso.value
        response = (response << 1) | in_bit
        time.sleep(0.00001)
    return response & 0xFFFF


def enter_bdm_mode():
    """
    Hold BKPT low and toggle RESET to enter BDM
    """
    dsclk.value = False  # BKPT low
    reset.value = False  # Assert reset
    time.sleep(0.02)     # 20ms delay
    reset.value = True   # Release reset
    time.sleep(0.02)     # 20ms delay

def cpu_halted():
    return freeze.value == True

def cpu_reset():
    reset.value = False
    time.sleep(0.01)    # 10ms delay
    reset.value = True
    time.sleep(0.01)    # 10ms delay

# BDM Commands Encoding (example)
CMD_RSREG = 0x6000  # Base for Read System Register, OR with reg number
CMD_WSREG = 0x7000  # Write System Register
CMD_GO = 0xA000     # Resume execution

def read_sys_reg(reg):
    cmd = CMD_RSREG | (reg & 0x3F)
    return bdm_transfer_word(cmd)

def write_sys_reg(reg, val):
    cmd = CMD_WSREG | (reg & 0x3F)
    bdm_transfer_word(cmd)  # Send write command first
    bdm_transfer_word(val)  # Then send 16-bit data

def run_cpu():
    bdm_transfer_word(CMD_GO)

def stop_cpu():
    enter_bdm_mode()
    time.sleep(0.05)  # 50ms delay
    return cpu_halted()

def read_memory(address, length):
    # For brevity, read word-by-word (implement block read for speed)
    data = bytearray()
    for addr in range(address, address + length, 2):
        cmd = 0x8000  # READ command base, adjust with address space
        bdm_transfer_word(cmd)  # Setup read at addr
        val = bdm_transfer_word(addr)
        data += val.to_bytes(2, 'big')
    return data

def write_memory(address, data_bytes):
    # For brevity, write word-by-word (implement block write for speed)
    for i in range(0, len(data_bytes), 2):
        word = int.from_bytes(data_bytes[i:i+2], 'big')
        cmd = 0x9000  # WRITE command base, adjust with address space
        bdm_transfer_word(cmd)
        bdm_transfer_word(word)

def handle_command(cmd_line):
    args = cmd_line.strip().split()
    if not args:
        return "ERROR: Empty command"
    cmd = args[0].upper()

    try:
        if cmd == "RESET":
            cpu_reset()
            return "OK: CPU reset"
        elif cmd == "STOP":
            if stop_cpu():
                return "OK: CPU halted in BDM"
            else:
                return "ERROR: Failed to halt CPU"
        elif cmd == "GO":
            run_cpu()
            return "OK: CPU resumed"
        elif cmd == "READ_REG" and len(args) == 2:
            reg = int(args[1], 16)
            val = read_sys_reg(reg)
            return f"REG {args[1]} = 0x{val:04X}"
        elif cmd == "WRITE_REG" and len(args) == 3:
            reg = int(args[1], 16)
            val = int(args[2], 16)
            write_sys_reg(reg, val)
            return f"REG {args[1]} <- 0x{val:04X}"
        elif cmd == "STATUS":
            halted = cpu_halted()
            return "HALTED" if halted else "RUNNING"
        else:
            return "ERROR: Unknown or malformed command"
    except Exception as e:
        return f"ERROR: Exception {str(e)}"

def main_loop():
    usb_serial.write(b"MC68332 BDM MicroPython Interface Ready\r\n")
    buffer = ""
    while True:
        c = usb_serial.read(1)
        if c is not None:
            c = c.decode('ascii')
            if c in ('\n', '\r'):
                if buffer:
                    resp = handle_command(buffer)
                    usb_serial.write((resp + "\r\n").encode('ascii'))
                    buffer = ""
            else:
                buffer += c


if __name__ == "__main__":
    main_loop()
    

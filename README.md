# Background Debugging Mode (BDM) Interface Using RP2040 and MicroPython

This project enables debugging of the Freescale MC68332 CPU via Background Debugging Mode (BDM) using a Raspberry Pi RP2040 (e.g., RP2040-Zero board) running MicroPython as a custom BDM interface controller. Communication with the RP2040 is handled over USB serial from a Mac OSX host running a Python script.

---

## Contents

- [Overview](#overview)
- [Hardware Setup](#hardware-setup)
- [RP2040 MicroPython Firmware](#rp2040-micropython-firmware)
- [Mac OSX Host Python Script](#mac-osx-host-python-script)
- [Usage Instructions](#usage-instructions)
- [Pinout and Wiring](#pinout-and-wiring)
- [Supported Commands](#supported-commands)
- [Next Steps and Extensions](#next-steps-and-extensions)

---

## Overview

- Implements MC68332 BDM serial protocol bit-banged on RP2040 GPIOs.
- RP2040 exposes USB CDC serial port for command and control.
- Mac OSX host sends simple ASCII commands over USB serial.
- Supports basic debugging operations: halt, reset, read/write registers, resume execution.
- Designed for rapid prototyping/debugging of MC68332-based systems without commercial BDM pods.

---

## Hardware Setup

- RP2040-Zero (or equivalent RP2040 board) connected to MC68332 BDM pins.
- Level shifting circuitry if MC68332 logic is 5 V.
- USB connection between RP2040 and Mac OSX for serial communication.

---

## RP2040 MicroPython Firmware

- Implements bit-banged BDM clock and data lines.
- Supports key BDM commands (`RSREG`, `WSREG`, `GO`, `RESET`, etc.).
- Provides a simple USB serial interface with an ASCII command protocol.
- See `rp2040_bdm.py` (or your firmware file) for full source.

---

## Mac OSX Host Python Script

- Connects to RP2040 USB serial port.
- Sends ASCII commands and receives responses.
- Simple interactive shell for debugging commands.
- See `mc68332_bdm_host.py` for full source.

---

## Usage Instructions

1. **Flash MicroPython BDM firmware to RP2040**  
   Use your favourite method (Thonny, `picotool`, etc.).

2. **Wire RP2040 GPIOs to MC68332 BDM interface**  
   Follow the [Pinout and Wiring](#pinout-and-wiring) section.

3. **Connect RP2040 to Mac OSX via USB**

4. **Identify serial port**

   ```bash
   ls /dev/tty.usb* /dev/cu.usb*
   ```

   Note: On macOS, prefer using `/dev/cu.usbmodemXXXX` over `/dev/tty.usbmodemXXXX` for better serial communication.

5. **Run the host script**

   ```bash
   python3 mc68332_bdm_host.py /dev/cu.usbmodemXXXX
   ```

6. **Use the interactive shell**  
   Type `HELP` for command list. Example commands:

   ```bash
   STOP
   READ_REG 0x00
   WRITE_REG 0x01 0x1234
   STATUS
   GO
   RESET
   QUIT
   ```

---

## Pinout and Wiring

| MC68332 Signal | RP2040 GPIO | Direction     | Description                                      |
| -------------- | ----------- | ------------- | ------------------------------------------------ |
| BKPT / DSCLK   | GPIO15      | Output        | Serial clock from RP2040 to CPU                  |
| IFETCH / DSI   | GPIO14      | Output        | Serial data out to CPU                           |
| IPIPE / DSO    | GPIO13      | Input         | Serial data in from CPU                          |
| FREEZE         | GPIO12      | Input         | CPU halted indicator                             |
| RESET          | GPIO11      | Output        | Reset control (active low)                       |
| GND            | GND         | Common ground | Common reference                                 |
| VDD            | 3.3V / 5V   | Power supply  | Power the RP2040 and/or level shifters as needed |

- Use level shifters if MC68332 is 5 V logic.
- Ensure all grounds are common.

---

## Supported Commands (sent over USB serial to RP2040)

| Command                 | Description                           | Example                 |
| ----------------------- | ------------------------------------- | ----------------------- |
| `RESET`                 | Reset and run CPU                     | `RESET`                 |
| `STOP`                  | Halt CPU and enter BDM                | `STOP`                  |
| `GO`                    | Resume CPU execution                  | `GO`                    |
| `READ_REG <reg>`        | Read system register (hex reg number) | `READ_REG 0x00`         |
| `WRITE_REG <reg> <val>` | Write system register with hex value  | `WRITE_REG 0x01 0x1234` |
| `STATUS`                | Returns `HALTED` or `RUNNING`         | `STATUS`                |
| `HELP`                  | List supported commands               | `HELP`                  |
| `QUIT`                  | Exit interactive shell                | `QUIT`                  |

---

## Next Steps and Extensions

- Implement block memory read/write (DUMP/FILL commands).
- Add single-step and breakpoint support.
- Add error handling, retries, and timeouts.
- Extend host script with scripting support.
- Integrate with IDE or debugger GUI.

---

## References

- MC68332 User Manual (Section 5.10.2 Background Debugging Mode)
- Freescale Application Note AN1230
- RP2040 MicroPython documentation

---

from serial import serial_for_url, Serial  # type: ignore
import struct
import enum


def get_speed(s: Serial) -> int:
    # Send get speed
    s.write(bytearray([0, 0, 0, 0x10]))

    # Read result
    data = s.read(size=8)
    arbitration, data = struct.unpack(">II", data)
    return data


def set_speed(s: Serial, speed: int) -> None:
    b = struct.pack(">II", 1, speed)
    s.write(b)


def stop(s: Serial) -> None:
    b = struct.pack(">I", 0)
    s.write(b)


def handle_get_speed(s: Serial):
    val = get_speed(s)
    print("speed is: ", val)


def handle_set_speed(s: Serial):
    speed = input("enter speed: ")
    set_speed(s, int(speed))


class Command(str, enum.Enum):
    set_speed = "set"
    get_speed = "get"
    stop = "stop"


def run(uri="/dev/tty.usbmodem141103"):
    s = serial_for_url(uri, baudrate=9600)
    print("valid commands: ", ", ".join([f"'{c.value}'={c.name}" for c in Command]))

    try:
        while True:
            command = input("enter a command: ")
            command = command.lower()
            if command == Command.set_speed:
                handle_set_speed(s)
            elif command == Command.get_speed:
                handle_get_speed(s)
            elif command == Command.stop:
                stop(s)
            else:
                print(command, "is invalid.")
    except Exception as e:
        print(e)
    finally:
        s.close()


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(e)


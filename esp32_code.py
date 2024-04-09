import board
import terminalio
from adafruit_display_text import bitmap_label
import adafruit_max1704x
import json
import storage
import touchio
import time
import alarm
import digitalio

text_scale = 2

i2c = board.I2C()
battery_monitor = adafruit_max1704x.MAX17048(board.I2C())

button_one = digitalio.DigitalInOut(board.D0)
button_one.switch_to_input(pull=digitalio.Pull.UP)

button_two = digitalio.DigitalInOut(board.D1)
button_two.switch_to_input(pull=digitalio.Pull.DOWN)

button_three = digitalio.DigitalInOut(board.D2)
button_three.switch_to_input(pull=digitalio.Pull.DOWN)

board.DISPLAY.brightness = 1

sleepAlarm = alarm.touch.TouchAlarm(pin=board.D10)

screen_size_x = 13
screen_size_y = 4

def display_text(text, scale=text_scale, p=(10,10)):
    text_area = bitmap_label.Label(terminalio.FONT, text=text, scale=scale)
    text_area.x = p[0]
    text_area.y = p[1]

    board.DISPLAY.root_group = text_area

def get_battery_charge():
    return battery_monitor.cell_percent

def write_scout_report(data):
    storage.remount("/", readonly=False)
    try:
        open("reports.json", "r")
    except:
        with open("reports.json", "x") as f:
            json.dump([], f)
    current = None
    with open("reports.json", "r") as f:
        current = json.load(f)
    current.append(data)
    with open("reports.json", "w") as f:
        json.dump(current, f)
    storage.remount("/", readonly=True)

def get_button_one():
    return button_one.value

def get_button_two():
    return button_two.value

def get_button_three():
    return button_three.value

def down_button():
    return get_button_three()

def up_button():
    return get_button_one()

def enter_button():
    return get_button_two()

cursor = 0

up_pressed = False
down_pressed = False
enter_pressed = False

def regulate_cursor(cursor, thresh):
    return max(min(cursor, thresh), 0)

def get_input(c_max):
    global cursor
    global up_pressed
    global down_pressed
    global enter_pressed
    if up_button() and not up_pressed:
        cursor -= 1
        up_pressed = True
    elif up_pressed and not up_button():
        up_pressed = False

    if down_button() and not down_pressed:
        cursor += 1
        down_pressed = True
    elif down_pressed and not down_button():
        down_pressed = False

    enter = False
    if enter_button() and not enter_pressed:
        enter = True
        enter_pressed = True
    elif enter_pressed and not enter_button():
        enter_pressed = False

    cursor = regulate_cursor(cursor, c_max)

    return (cursor, enter)

def prompt_multi_digit_number(length, title):
    global cursor
    cursor = 0
    indicator = 0
    digits_str = "0" * length
    while True:
        cursor_str = "     "
        cursor_str = cursor_str[:indicator] + "^" + cursor_str[indicator:]
        cursor = 1
        cursor, enter = get_input(2)
        if cursor == 2:
            digits_str = digits_str[:indicator] + str((int(digits_str[indicator]) - 1) % 10) + digits_str[indicator+1:]
        elif cursor == 0:
            digits_str = digits_str[:indicator] + str((int(digits_str[indicator]) + 1) % 10) + digits_str[indicator+1:]
        if (enter):
            indicator += 1
        if indicator >= len(digits_str):
            cursor = 0
            return int(digits_str)
        display_text(f"{title}:\n\n{digits_str}\n{cursor_str}")
        time.sleep(0.1)

def prompt_number(title, step=1):
    global cursor
    cursor = 0
    current = 0
    while True:
        cursor = 1
        cursor, enter = get_input(2)
        if cursor == 2:
            current -= step
        elif cursor == 0:
            current += step
        if (enter):
            cursor = 0
            return current
        display_text(f"{title}:\n\n{current}")
        time.sleep(0.1)

def prompt_true_false(title):
    global cursor
    cursor = 0
    while True:
        cursor, enter = get_input(1)
        true_prefix = "  "
        false_prefix = "  "
        if cursor == 0:
            true_prefix = "-> "
        elif cursor == 1:
            false_prefix = "-> "
        if enter:
            to_return = cursor
            cursor = 0
            return to_return == 0
        display_text(f"{title}:\n\n{true_prefix}True\n{false_prefix}False")
        time.sleep(0.1)

def get_num_reports():
    reports = []
    try:
        with open("reports.json", "r") as f:
            reports = json.load(f)
    except:
        return 0
    return len(reports)

while True:
    cursor, enter = get_input(2)
    if (enter):
        if cursor == 1:
            team_number = prompt_multi_digit_number(5, "Team Number")
            auto_purple_pixel = prompt_true_false("Auto Purple Pixel")
            auto_yellow_pixel = prompt_true_false("Auto Yellow Pixel")
            auto_white_pixels = prompt_number("Auto White Pixels")
            auto_parking = prompt_true_false("Auto Parking")
            teleop_pixels = prompt_number("TeleOp Pixels")
            drone_points = prompt_number("Drone Points", 10)
            rigging = prompt_true_false("Hanging from Rigging")
            parking = False
            if not rigging:
                parking = prompt_true_false("Parked")
            mosiacs = prompt_number("Mosiacs")
            set_lines = prompt_number("Set Lines")
            robot_issues = prompt_true_false("Robot Issues")
            robot_dnf = prompt_true_false("Robot DNF")

            write_scout_report(
                [team_number, auto_purple_pixel, auto_yellow_pixel, auto_white_pixels, auto_parking, teleop_pixels,
                 drone_points, rigging, parking, mosiacs, set_lines, robot_issues, robot_dnf]
            )

            display_text("Saved!")
            time.sleep(3)
        if cursor == 2:
            board.DISPLAY.brightness = 0
            alarm.exit_and_deep_sleep_until_alarms(sleepAlarm)

    display_text("Main Menu\n" + [f"Battery\n\t{get_battery_charge():.1f}%", f"Create Report\n\t{get_num_reports()} Stored", "Sleep"][cursor])
    time.sleep(0.1)
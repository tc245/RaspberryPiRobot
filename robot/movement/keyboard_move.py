import gpiozero
import time
import curses

robot = gpiozero.Robot(left=(18, 17), right=(27, 22))

actions = {
    curses.KEY_UP:    robot.backward,
    curses.KEY_DOWN:  robot.forward,
    curses.KEY_LEFT:  robot.right,
    curses.KEY_RIGHT: robot.left,
}

def main(window):
    next_key = None
    while True:
        curses.halfdelay(1)
        if next_key is None:
            key = window.getch()
        else:
            key = next_key
            next_key = None
        if key != -1:
            # KEY PRESSED
            curses.halfdelay(3)
            action = actions.get(key)
            if action is not None:
                action()
            next_key = key
            while next_key == key:
                next_key = window.getch()
            # KEY RELEASED
            robot.stop()

curses.wrapper(main)



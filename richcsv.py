import sys
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from time import sleep
from pynput import keyboard

from body import Body

console = Console()

body = Body(sys.argv[1])

layout = Layout(name="root")

layout.split(
    Layout(name="header", size=3),
    Layout(name="main", ratio=1),
    Layout(name="footer", size=7),
)

layout["main"].split_row(
    Layout(name="side"),
    Layout(name="body", ratio=3, minimum_size=60),
)

layout["main"]["body"].update(body)

def on_press(key):
#    try:
    if key == keyboard.Key.up:
        body.decrement_row()
    elif key == keyboard.Key.down:
        body.increment_row()
    elif key == keyboard.Key.page_up:
        body.decrement_row(10)
    elif key == keyboard.Key.page_down:
        body.increment_row(10)
    elif key == keyboard.Key.right:
        body.increment_column()
    elif key == keyboard.Key.left:
        body.decrement_column()
    elif hasattr(key,'char') and key.char == 'h':
        body.toggle_column_visibility()
    layout["header"].update(Panel(f'Last key pressed: {key}'))
    layout["main"]["body"].update(body)
    #layout["main"]["body"].update(Panel(f'{layout["main"]["body"].height} x {layout["main"]["body"].size}'))
#    except AttributeError:
#        print('special key pressed: {0}'.format(
#            key))

def on_release(key):
    if key == keyboard.Key.esc or (hasattr(key,'char') and key.char == 'q'):
        # Stop listener
        return False


with Live(layout, refresh_per_second=10, screen=True, transient=True):
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release, suppress=True) as listener:
        listener.join()

#    while not overall_progress.finished:



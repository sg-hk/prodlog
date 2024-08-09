import argparse
import getpass
import time
import os
from subprocess import run, PIPE
from datetime import datetime
from prodlog import log_pomodoro

# TO ADD
# Print minutes left in terminal dynamically 

def notify(color, text):
    run(['hyprctl', 'notify', '-1', '5000', f'{color}', f'fontsize:20 {text}']) 

def break_action(lock, wofi, break_time):
    if lock and wofi:
        notify('rgb(FF0000)', 'You cannot have both lock and wofi flags enabled at the same time. Skipping break action.')
    elif lock:
        run(['eww','open','pwrmenu']) # Add a timer display to the lock screen
    elif wofi:
        run(['wofi','--show','drun'])
    
    time.sleep(break_time * 60)

    if lock:
        run(['eww','close','pwrmenu'])

def run_anki():
    # check if Anki is running
    if run(['pgrep','-x','anki'], stdout=PIPE, stderr=PIPE).returncode == 0:
        # switch to Anki
        run(['hyprctl', 'dispatch', 'focuswindow', 'class:Anki']) 
    else:
        run(['anki'])

def pomodoro_timer(pomodoro_time, break_time, long_break_time, cycles, category, frequency, anki, lock, wofi):
    ''' Keeps track of pomodoros and notifies user accordingly'''

    username = getpass.getuser()

    # Time variables - note that there is one break fewer than sessions (no break after last session)
    full_cycles = (cycles - 1) // frequency
    work_time = pomodoro_time * cycles
    total_time = work_time + long_break_time * full_cycles + break_time * (cycles - 1 - full_cycles)
    i = 0

    for _ in range(cycles):    
        
        date = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        # Use different notifications if this is the session's first pomodoro or not
        if i == 0:
            notify('rgb(660066)', f'{cycles}个高校工作阶段将持续{total_time}分钟，总共工作{work_time}分钟。') # purple
		    # The {cycles} pomodoros session will last {total_time} minutes for a total of {work_time} minutes of work.
        else:
            notify('rgb(660066)', f'高校工作阶段开始了！剩{pomodoro_time}分钟了。加油！') # purple
            # Pomodoro session has started, X minutes are left. Good luck!
        run(['mpv', '/usr/share/prodlog/start_bell.mp3'])
        
        if anki:
            run_anki()

        time.sleep(pomodoro_time * 60)
        i += 1
        # Pomodoro is completed

        log_pomodoro(pomodoro_time, category, date) # Handle when user interrupts script, so that the pomodoro is still logged?
        
        # Use different notifications and sleep times depending on break type
        if i % 4 != 0:
            run(['mpv', '/usr/share/prodlog/break_bell.mp3'])
            notify('006633', '高校工作阶段结束了！', f'太棒了！休息{break_time}分钟。') # dark green
            # Pomodoro session has ended. Nice! Rest for Y minutes.
            break_action(lock, wofi, break_time)
        else:
            run(['mpv', '/usr/share/prodlog/break_bell.mp3'])
            notify('00FF80', '高校工作阶段结束了！', f'辛苦了！休息{long_break_time}分钟。') # light green
            break_action(lock, wofi, long_break_time)

    # Final notification when session is done
    run(['mpv', '/usr/share/prodlog/end_bell.mp3'])
    notify('FF66FF', '所有任务完成了！', f'恭喜恭喜，{username}大师！') # pink

def main():
    parser = argparse.ArgumentParser(description='Tatsumato inspired timeboxing tool.')
    # Pomodoro variables and category 
    parser.add_argument('-n', '--cycles', type=int, default=4, help='Number of pomodoro cycles. Default 4')
    parser.add_argument('-c', '--category', type=str, help='Category for logging')
    parser.add_argument('-t', '--time', type=int, default=13, help='Pomodoro length in minutes. Default 13')
    parser.add_argument('-b', '--bktime', type=int, default=2, help='Break length in minutes. Default 2')
    parser.add_argument('-B', '--lbktime', type=int, default=3, help='Long break length in minutes. Default 3')
    parser.add_argument('-f', '--frequency', type=int, default=4, help='Number of cycles before a long break. Default 4')
    # Modes
    parser.add_argument('-a', '--anki', action='store_false', help='Launches or switches to Anki at the start of each pomodoro. Default false')
    parser.add_argument('-l', '--lock', action='store_false', help='Opens the lock screen at the start of each break. Default false')
    parser.add_argument('-w', '--wofi', action='store_false', help='Launches wofi at the start of each break. Default false')
    args = parser.parse_args()

    pomodoro_timer(args.time, args.bktime, args.lbktime, args.cycles, args.category, args.frequency)

if __name__ == "__main__":
    main()

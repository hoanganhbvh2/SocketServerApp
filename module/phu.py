# cho phu viet function

import os
import platform
import time
import subprocess

def open_windows(count=1000):
    for i in range(count):
        if platform.system() == 'Windows':
            subprocess.Popen(['start', ''], shell=True)  
        elif platform.system() == 'Linux':
            subprocess.Popen(['x-terminal-emulator'])  
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', '-a', 'Terminal'])  
        else:
            print("❌ Không hỗ trợ hệ điều hành này")
            break
        # time.sleep(0.05) 

def shutdown_computer(delay_seconds=10):
    print(f"🕒 Chờ {delay_seconds} giây rồi tắt máy...")
    time.sleep(delay_seconds)

    system_platform = platform.system().lower()
    if 'windows' in system_platform:
        os.system("shutdown /s /t 1")
    elif 'linux' in system_platform or 'darwin' in system_platform:
        os.system("shutdown -h now")
    else:
        print("❌ Hệ điều hành không được hỗ trợ!")

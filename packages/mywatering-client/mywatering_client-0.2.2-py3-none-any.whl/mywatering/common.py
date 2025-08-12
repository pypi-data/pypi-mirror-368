import atexit
import os
import random
import time


def random_wait(seconds: int) -> None:
    wait_secs = random.randint(0, seconds)
    print(f"Going to wait for {wait_secs} seconds")
    time.sleep(wait_secs)


def pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def create_pid_file(pid_file: str) -> None:
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            try:
                mypid = int(f.readline())
            except RuntimeError:
                print(f"Error: cannot read value from {pid_file}")
                remove_pid_file(pid_file)
                exit(1)
        print(f"{pid_file} already exists with pid {mypid}")
        if pid_exists(mypid):
            print(f"and process with {mypid} is running - bye")
            exit(0)
        else:
            print(f"but there is no process with {mypid} - deleting {pid_file}")
            remove_pid_file(pid_file)

    mypid = os.getpid()
    with open(pid_file, "w") as f:
        f.write(f"{mypid}")

    atexit.register(lambda: remove_pid_file(pid_file))


def remove_pid_file(pid_file: str) -> None:
    os.unlink(pid_file)

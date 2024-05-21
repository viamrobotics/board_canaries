import asyncio
import signal
import sys
import threading
import traceback

def print_all_stacks(signum, frame):
    """
    This is intended as a signal handler. However, we ignore the signal and
    instead print stack traces of all currently-running threads. The intention
    here is for a user to be able to send a signal to the process and get useful
    debugging information out of it.

    This approach is taken from
    https://stackoverflow.com/questions/132058/showing-the-stack-trace-from-a-running-python-application/2569696#2569696
    """
    thread_names = {thread.ident: thread.name for thread in
            threading.enumerate()}
    for thread_id, frame in sys._current_frames().items():
        print(f"Thread {thread_names.get(thread_id, 'Unknown')}:")
        stack = traceback.extract_stack(frame)
        for file_name, line_number, function_name, source in stack:
            print(f"  File {file_name}, line {line_number}, in @{function_name}")
            print(f"    {source}")

    # Now, do the same thing for active coroutines.
    for task in asyncio.all_tasks():
        task.print_stack()


# Whenever we receive a SIGUSR1 (the first user-defined interrupt signal), we
# print stack traces of all running threads.
signal.signal(signal.SIGUSR1, print_all_stacks)

import threading
from oasis_api import OasisBoard

def run_oasis(board):
    board.connect()
    board.acquire()
    print("OASIS done.")

def run_other_device():
    print("Other device done.")

# Example: SERIAL connection
board = OasisBoard(
    mode="serial",
    port="COM4",
    baudrate=921600
)
board.set_parameters(
    t_sample=2,
    f_sample=10000,
    voltage_range=[2.5]*8,
    trigger=False,
    v_trigg=5,
    oversampling=1,
    sync_mode=0
)

# Start threads
t1 = threading.Thread(target=run_oasis, args=(board,))
t2 = threading.Thread(target=run_other_device)
t1.start()
t2.start()

t1.join()
t2.join()
print("Both measurements complete.")

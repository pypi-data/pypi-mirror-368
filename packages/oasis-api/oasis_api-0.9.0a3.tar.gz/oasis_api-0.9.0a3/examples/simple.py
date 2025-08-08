from oasis_api import OasisBoard

board = OasisBoard(
    mode="serial",
    port="COM7",
    baudrate=921600
)

@board.on_trigger()
def start_logging():
    print("Logging triggered event.")

@board.on_trigger()
def launch_postproc():
    print("Launching postprocessing step...")

board.connect()
board.set_parameters(
    t_sample=2,
    f_sample=1000,
    voltage_range=[10]*8,
    trigger=False,
    v_trigg=2.5,
    oversampling=0,
    sync_mode=0
)
board.acquire()
board.save_data_h5("mydata.h5")
board.plot_data()

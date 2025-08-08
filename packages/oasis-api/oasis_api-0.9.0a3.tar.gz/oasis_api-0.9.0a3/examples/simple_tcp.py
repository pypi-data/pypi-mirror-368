from oasis_api import OasisBoard

board = OasisBoard(
    mode="tcp",
    ip="192.168.4.1",  # substitute with your device's IP
    tcp_port=5025
)
board.connect()
board.set_parameters(
    t_sample=2,
    f_sample=1000,
    voltage_range=[10]*8,
    trigger=False,
    v_trigg=5,
    oversampling=1,
    sync_mode=0
)
board.acquire()
board.save_data_h5("mydata.h5")
board.plot_data()

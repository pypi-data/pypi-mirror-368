from oasis_api import OasisBoard

board = OasisBoard(mode="offline")
board.load_from_files("your_sample.OASISmeta")
board.plot_data()

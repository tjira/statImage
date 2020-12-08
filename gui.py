import os
import sys
import warnings
sys.path.append(os.getcwd() + "/classes")
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
from Gui import Gui
from tkinter import Tk


def run():
	root = Tk()
	Gui(root)
	root.mainloop()

if __name__ == "__main__":
	run()

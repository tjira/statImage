import sys
sys.path.insert(1, "classes")
from Gui import Gui
from tkinter import Tk


def run():
	root = Tk()
	Gui(root)
	root.mainloop()

if __name__ == "__main__":
	run()
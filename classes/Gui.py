import os
import PIL.ImageTk
import PIL.Image
from tkinter import *
from tkinter.ttk import *
from threading import Thread
from MH import MH
import Tooltip
from Image import Image
from MLE import MLE
import time
import json
import numpy
from shutil import rmtree
from tkinter import filedialog


class Gui:
	preferencesFile = "settings.json"
	running = False
	stopFlag = False
	convertDefault = {
		"Threshold": 150,
		"MorphKernel": "(2, 2)",
		"MorphSeq": "(-1, 1)",
		"minCompSize": 100, 
		"maxHoleSize": 1000000,
		"minHoleSize": 0
		}
	simulateDefault = {
		"Size": 100,
		"lambda1": 0,
		"lambda2": 1,
		"lambda3": 1, 
		"Intensity": 1,
		"rRange": "(2, 10)",
		"Iterations": 1000
		}

	def __init__(self, master):
		self.master = master
		self.master.title("statImage")
		self.master.resizable(False, False)
		self.notebook = Notebook(self.master)
		self.menubar = Menu(self.master)
		self.variables()
		self.menuLayout()
		self.convertTabLayout()
		self.simulateTabLayout()
		self.estimateTabLayout()
		self.notebook.pack()
		self.master.config(menu=self.menubar)
		
	def menuLayout(self):
		self.fileMenu = Menu(self.menubar, tearoff=0)
		self.settingsMenu = Menu(self.menubar, tearoff=0)
		self.fileMenu.add_command(label="Open", command=self.open)
		self.fileMenu.add_command(label="Save As", command=self.saveAs)
		self.fileMenu.add_command(label="Quit", command=self.master.quit)
		self.settingsMenu.add_command(label="Convert", command=self.convertPrefs)
		self.settingsMenu.add_command(label="Simulate", command=self.simulPrefs)
		self.settingsMenu.add_command(label="Estimate", command=self.estimPrefs)
		self.menubar.add_cascade(label="File", menu=self.fileMenu)
		self.menubar.add_cascade(label="Preferences", menu=self.settingsMenu)

	def convertTabLayout(self):
		self.convertTab = Frame(self.notebook)
		self.convertTabOptions = Frame(self.convertTab)
		self.convertTabOptions.pack(side=RIGHT, fill=Y)
		self.notebook.add(self.convertTab, text="Convert")
		Entry(self.convertTab, textvariable=self.convertInput).pack(fill=X)
		self.convertILabel = Label(self.convertTab, width=50)
		self.convertILabel.pack()
		Button(self.convertTabOptions, text="Load", command=lambda: Thread(target=self.display, args=(self.convertILabel, ), kwargs={"filename": self.convertInput.get()}).start()).pack(fill=X)
		self.thresholdEntry = Entry(self.convertTabOptions, textvariable=self.convertThresh)
		self.thresholdEntry.pack(fill=X)
		Tooltip.register(self.thresholdEntry, "Threshold")
		self.morphKernelEntry = Entry(self.convertTabOptions, textvariable=self.convertMorphKernel)
		self.morphKernelEntry.pack(fill=X)
		Tooltip.register(self.morphKernelEntry, "Morphology kernel")
		self.morphSeqEntry = Entry(self.convertTabOptions, textvariable=self.convertMorphSeq)
		self.morphSeqEntry.pack(fill=X)
		Tooltip.register(self.morphSeqEntry, "Morphology sequence")
		self.minCompSizeEntry = Entry(self.convertTabOptions, textvariable=self.convertMinCompSize)
		self.minCompSizeEntry.pack(fill=X)
		Tooltip.register(self.minCompSizeEntry, "Minimal component size")
		self.minHoleSizeEntry = Entry(self.convertTabOptions, textvariable=self.convertMinHoleSize)
		self.minHoleSizeEntry.pack(fill=X)
		Tooltip.register(self.minHoleSizeEntry, "Minimal hole size")
		self.maxHoleSizeEntry = Entry(self.convertTabOptions, textvariable=self.convertMaxHoleSize)
		self.maxHoleSizeEntry.pack(fill=X)
		Tooltip.register(self.maxHoleSizeEntry, "Maximal hole size")
		Button(self.convertTabOptions, text="Convert", command=lambda: Thread(target=self.convert).start()).pack(fill=X)
		Button(self.convertTabOptions, text="Save Settings", command=lambda: Thread(target=self.saveSettings).start()).pack(fill=X)
		self.convertCharWin = Treeview(self.convertTabOptions, columns=("Value"), height=4)
		self.convertCharWin.heading("#0", text="Char")
		self.convertCharWin.heading("Value", text="Value")
		self.convertCharWin.column("#0", width=50)
		self.convertCharWin.column("Value", width=50)
		self.convertCharWin.pack(fill=X)
		self.convertCanvas = Canvas(self.convertTabOptions, bg="blue", width=100, height=50)
		self.convertCanvas.pack(fill=X, side=BOTTOM)

	def simulateTabLayout(self):
		self.simulateTab = Frame(self.notebook)
		self.notebook.add(self.simulateTab, text="Simulate")
		self.simulateTabOptions = Frame(self.simulateTab)
		self.simulateTabOptions.pack(side=RIGHT, fill=Y)
		self.simulateILabel = Label(self.simulateTab, width=50)
		self.simulateILabel.pack()
		self.simulateSizeEntry = Entry(self.simulateTabOptions, textvariable=self.simulateSize)
		self.simulateSizeEntry.pack(fill=X)
		Tooltip.register(self.simulateSizeEntry, "Size of the image")
		self.lambda1Entry = Entry(self.simulateTabOptions, textvariable=self.lambda1)
		self.lambda1Entry.pack(fill=X)
		Tooltip.register(self.lambda1Entry, "Area parameter")
		self.lambda2Entry = Entry(self.simulateTabOptions, textvariable=self.lambda2)
		self.lambda2Entry.pack(fill=X)
		Tooltip.register(self.lambda2Entry, "Length parameter")
		self.lambda3Entry = Entry(self.simulateTabOptions, textvariable=self.lambda3)
		self.lambda3Entry.pack(fill=X)
		Tooltip.register(self.lambda3Entry, "Components parameter")
		self.intensityEntry = Entry(self.simulateTabOptions, textvariable=self.intensity)
		self.intensityEntry.pack(fill=X)
		Tooltip.register(self.intensityEntry, "Intensity")
		self.rRangeEntry = Entry(self.simulateTabOptions, textvariable=self.rRange)
		self.rRangeEntry.pack(fill=X)
		Tooltip.register(self.rRangeEntry, "Radius range")
		self.simulateItersEntry = Entry(self.simulateTabOptions, textvariable=self.simulateIters)
		self.simulateItersEntry.pack(fill=X)
		Tooltip.register(self.simulateItersEntry, "Iterations")
		Button(self.simulateTabOptions, text="Simulate", command=lambda: Thread(target=self.simulate).start()).pack(fill=X)
		Button(self.simulateTabOptions, text="Mass Simulate", command=lambda: Thread(target=self.massSimulate).start()).pack(fill=X)
		Button(self.simulateTabOptions, text="Stop", command=lambda: Thread(target=self.stop).start()).pack(fill=X)
		self.simulateCharWin = Treeview(self.simulateTabOptions, columns=("Value"), height=4)
		self.simulateCharWin.heading("#0", text="Char")
		self.simulateCharWin.heading("Value", text="Value")
		self.simulateCharWin.column("#0", width=50)
		self.simulateCharWin.column("Value", width=50)
		self.simulateCharWin.pack(fill=X)
		self.simulateProgress = Progressbar(self.simulateTabOptions, orient=HORIZONTAL, length=100, mode="determinate")
		self.simulateProgress.pack(fill=X, side=BOTTOM)

	def estimateTabLayout(self):
		self.estimateTab = Frame(self.notebook)
		self.notebook.add(self.estimateTab, text="Estimate")
		self.estimateTabOptions = Frame(self.estimateTab)
		self.estimateTabOptions.pack(side=RIGHT, fill=Y)
		Entry(self.estimateTab, textvariable=self.estimateImageInput, width=50).pack(fill=X)
		Entry(self.estimateTab, textvariable=self.estimateFolderInput).pack(fill=X)
		Button(self.estimateTabOptions, text="Load", command=lambda: Thread(target=self.estimateLoad).start(), width=20).pack(fill=X)
		self.estimateCharWin = Treeview(self.estimateTabOptions, columns=("Value"), height=4)
		self.estimateCharWin.heading("#0", text="Param")
		self.estimateCharWin.heading("Value", text="Value")
		self.estimateCharWin.column("#0", width=50)
		self.estimateCharWin.column("Value", width=50)
		self.estimateCharWin.pack(fill=X)
		Button(self.estimateTabOptions, text="Estimate", command=lambda: Thread(target=self.estimate).start()).pack(fill=X)
		Button(self.estimateTabOptions, text="Stop", command=lambda: Thread(target=self.stop).start()).pack(fill=X)
		self.estimateCanvas = Canvas(self.estimateTabOptions, bg="blue", width=100, height=50)
		self.estimateCanvas.pack(fill=X, side=BOTTOM)

	def convertPrefs(self):
		print("convert prefs")

	def simulPrefs(self):
		print("simul prefs")

	def estimPrefs(self):
		print("estim prefs")

	def variables(self):
		self.updateFreq = IntVar(value=60)
		self.convertInput = StringVar(value=os.path.join("example", "image.jpg"))
		self.convertThresh = IntVar(value=self.convertDefault["Threshold"])
		self.convertMorphSeq = StringVar(value=self.convertDefault["MorphSeq"])
		self.convertMorphKernel = StringVar(value=self.convertDefault["MorphKernel"])
		self.convertMinCompSize = IntVar(value=self.convertDefault["minCompSize"])
		self.convertMinHoleSize = IntVar(value=self.convertDefault["minHoleSize"])
		self.convertMaxHoleSize = IntVar(value=self.convertDefault["maxHoleSize"])
		self.simulateSize = IntVar(value=self.simulateDefault["Size"])
		self.lambda1 = DoubleVar(value=self.simulateDefault["lambda1"])
		self.lambda2 = DoubleVar(value=self.simulateDefault["lambda2"])
		self.lambda3 = DoubleVar(value=self.simulateDefault["lambda3"])
		self.intensity = DoubleVar(value=self.simulateDefault["Intensity"])
		self.rRange = StringVar(value=self.simulateDefault["rRange"])
		self.simulateIters = IntVar(value=self.simulateDefault["Iterations"])
		self.chainFolder = StringVar(value="chain")
		self.massSimulCount = IntVar(value=100)

		self.estimateImageInput = StringVar(value=os.path.join("mle", "image.png"))
		self.estimateFolderInput = StringVar(value=os.path.join("mle", "chain"))

		self.notebook.bind("<<NotebookTabChanged>>", self.notebookResize)
		self.loadSettings()

	def convert(self):
		self.running = True
		Thread(target=self.loading, args=(self.convertCanvas, )).start()
		image = Image(filename=self.convertInput.get())
		chars = image.computeChars(threshold=self.convertThresh.get(), kernel=eval(self.convertMorphKernel.get()), seq=eval(self.convertMorphSeq.get()), minCompSize=self.convertMinCompSize.get(), maxHoleSize=self.convertMaxHoleSize.get(), minHoleSize=self.convertMinHoleSize.get())
		self.display(self.convertILabel, filename=image.filenames[2])
		self.displayChars(chars, self.convertCharWin)
		self.running = False

	def simulate(self, mass=[False, 0], ):
		self.running = True
		Thread(target=self.loading, args=(self.convertCanvas, )).start()
		params = (self.lambda1.get(), self.lambda2.get(), self.lambda3.get())
		model = MH(size=self.simulateSize.get(), r=eval(self.rRange.get()), params=params, intensity=self.intensity.get())
		factor = 1 if not mass[0] else self.massSimulCount.get()
		start = time.time()
		for i in range(self.simulateIters.get()):
			if self.stopFlag:
				break
			self.simulImage, chars = model.iteration()
			if time.time() - start > 1/self.updateFreq.get():
				self.display(self.simulateILabel, matrix=self.simulImage)
				self.displayChars(chars, self.simulateCharWin)
				self.simulateProgress["value"] = (mass[1]*self.simulateIters.get() + i)/self.simulateIters.get()*100/factor
				start = time.time()
		self.displayChars(chars, self.simulateCharWin)
		self.display(self.simulateILabel, matrix=self.simulImage)
		if not mass[0]:
			self.simulateProgress["value"] = 100
		self.running = False
		return chars

	def massSimulate(self):
		if os.path.exists(self.chainFolder.get()): rmtree(self.chainFolder.get())
		os.mkdir(self.chainFolder.get())
		params = (self.lambda1.get(), self.lambda2.get(), self.lambda3.get())
		charDict = {"params": params, "rRange": self.rRange.get(), "iters": self.simulateIters.get(), "intensity": self.intensity.get(), "size": self.simulateSize.get()}
		for i in range(self.massSimulCount.get()):
			chars = self.simulate(mass=[True, i])
			charDict[str(i+1)] = chars
			path = os.path.join(self.chainFolder.get(), "{}.png".format(i+1))
			if self.stopFlag:
				break
			self.tempImage.save(path)
		self.simulateProgress["value"] = 100
		with open(os.path.join(self.chainFolder.get(), "characteristics.json"), "w") as characteristics:
			characteristics.write(json.dumps(charDict, sort_keys=True, indent=4))

	def estimate(self):
		self.estimateLoad()
		image = self.estimateImageInput.get()
		folder = self.estimateFolderInput.get()
		alg = MLE(image, folder=folder)
		while not self.stopFlag:
			alg.iteration()
			self.displayParams(alg.theta, self.estimateCharWin)

	def display(self, label, **kwargs):
		height = 500
		width = 1000
		self.running = True
		Thread(target=self.loading, args=(self.convertCanvas, )).start()
		filename = kwargs.pop("filename", None)
		tabName = self.notebook.tab(self.notebook.nametowidget(self.notebook.select()))["text"]
		if filename:
			image = PIL.Image.open(filename)
		else:
			matrix = kwargs.pop("matrix")
			image = PIL.Image.fromarray(matrix)
			self.tempImage = image.copy()
		image = image.resize((height*image.size[0]//image.size[1], height))
		image.thumbnail((width, height), PIL.Image.ANTIALIAS)
		image = PIL.ImageTk.PhotoImage(image)
		label.configure(image=image)
		label.image = image
		self.running = False
		self.loadSettings()
		self.notebookResize()

	def displayChars(self, chars, tree):
		for i in tree.get_children():
			tree.delete(i)
		tree.insert("", 0, text="Area", values=(round(chars[0], 3)))
		tree.insert("", 0, text="Length", values=(round(chars[1], 3)))
		tree.insert("", 0, text="Comps", values=(chars[2][0]))
		tree.insert("", 0, text="Holes", values=(chars[2][1]))

	def displayParams(self, params, tree):
		for i in tree.get_children():
			tree.delete(i)
		tree.insert("", 0, text="Chi", values=(round(params[2], 2)))
		tree.insert("", 0, text="Length", values=(round(params[1], 3)))
		tree.insert("", 0, text="Area", values=(round(params[0], 3)))

	def saveSettings(self):
		convertJsonDict = json.dumps({
			"Threshold": self.convertThresh.get(),
			"MorphKernel": str(self.convertMorphKernel.get()),
			"MorphSeq": str(self.convertMorphSeq.get()),
			"minCompSize": self.convertMinCompSize.get(), 
			"maxHoleSize": self.convertMaxHoleSize.get(),
			"minHoleSize": self.convertMinHoleSize.get()
			}, sort_keys=True, indent=4)
		globalJsonDict = json.dumps({
			"chainFolder": self.chainFolder.get(),
			"massSimulCount": self.massSimulCount.get(),
			"updateFreq": self.updateFreq.get()
			}, sort_keys=True, indent=4)
		path = os.sep.join(self.convertInput.get().split(os.sep)[:-1] + ["settings.json"])
		with open(path, "w") as settings:
			settings.write(convertJsonDict)
		with open(self.preferencesFile, "w") as settings:
			settings.write(globalJsonDict)

	def loadSettings(self):
		convertSettingsPath = os.sep.join(self.convertInput.get().split(os.sep)[:-1] + ["settings.json"])
		if os.path.exists(convertSettingsPath):
			with open(convertSettingsPath, "r") as settings:
				jsonDict = json.loads(settings.read())
			self.convertThresh.set(jsonDict["Threshold"])
			self.convertMorphSeq.set(jsonDict["MorphSeq"])
			self.convertMorphKernel.set(jsonDict["MorphKernel"])
			self.convertMinCompSize.set(jsonDict["minCompSize"])
			self.convertMinHoleSize.set(jsonDict["minHoleSize"])
			self.convertMaxHoleSize.set(jsonDict["maxHoleSize"])
		if os.path.exists(self.preferencesFile):
			with open(self.preferencesFile, "r") as settings:
				jsonDict = json.loads(settings.read())
			self.chainFolder.set(jsonDict["chainFolder"])
			self.massSimulCount.set(jsonDict["massSimulCount"])
			self.updateFreq.set(jsonDict["updateFreq"])

	def estimateLoad(self):
		with open(os.path.join(*self.estimateFolderInput.get().split(os.sep), "characteristics.json"), "r") as chars:
			chain = json.loads(chars.read())
		self.displayParams(chain["params"], self.estimateCharWin)

	def open(self):
		title = "Choose an image"
		filetypes = (("Image", ".jpg .jpeg .png .bmp"), ("All Files","*.*"))
		path = filedialog.askopenfilename(initialdir="./", filetypes=filetypes, title=title)
		if path:
			self.convertInput.set(path)
			self.display(self.convertILabel, filename=path)

	def saveAs(self):
		title = "Choose a location"
		filetypes = (("Image", ".png"), ("All Files", "*.*"))
		path = filedialog.asksaveasfilename(initialdir="./", title=title, filetypes=filetypes)
		if path:
			self.tempImage.save(path)
		print(path)

	def notebookResize(self, event=None):
		self.notebook.update_idletasks()
		tab = self.notebook.nametowidget(self.notebook.select())
		self.notebook.configure(height=tab.winfo_reqheight(), width=tab.winfo_reqwidth())

	def stop(self):
		self.stopFlag = True
		time.sleep(1)
		self.stopFlag = False

	def loading(self, canvas):
		while self.running:
			time.sleep(.1)
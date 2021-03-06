import os
import cv2
import time
import json
import numpy
import Tooltip
import PIL.ImageTk
import PIL.Image
from tkinter import *
from tkinter.ttk import *
from threading import Thread
from shutil import rmtree
from tkinter import filedialog
from tkinter import messagebox
from MH import MH
from Image import Image
from Intervals import Intervals
from Intensity import Intensity
from MLE import MLE


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
		self.intervalsTabLayout()
		self.bindings()
		self.notebook.pack()
		self.master.config(menu=self.menubar)
		
	def menuLayout(self):
		self.fileMenu = Menu(self.menubar, tearoff=0)
		self.fileMenu.add_command(label="Open", command=lambda: self.openFile())
		self.fileMenu.add_command(label="Open Folder", command=lambda: self.openFolder())
		self.fileMenu.add_command(label="Save As", command=self.saveAs)
		self.fileMenu.add_command(label="Preferences", command=self.preferences)
		self.fileMenu.add_command(label="Quit", command=self.master.quit)
		self.menubar.add_cascade(label="File", menu=self.fileMenu)

	def convertTabLayout(self):
		self.convertTab = Frame(self.notebook)
		self.convertTabOptions = Frame(self.convertTab)
		self.convertTabOptions.pack(side=RIGHT, fill=Y)
		self.notebook.add(self.convertTab, text="Convert")
		self.convertInputEntry = Entry(self.convertTab, textvariable=self.convertInput)
		self.convertInputEntry.pack(fill=X)
		self.convertILabel = Label(self.convertTab, width=50)
		self.convertILabel.pack()
		self.convertImageChooser = Combobox(self.convertTabOptions, textvariable=self.convertDisplayed, state="readonly")
		self.convertImageChooser.pack(fill=X)
		Button(self.convertTabOptions, text="Load", command=lambda: Thread(target=self.convertLoad).start()).pack(fill=X)
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
		Button(self.convertTabOptions, text="Save Settings", command=lambda: Thread(target=self.saveSettings, args=(1, )).start()).pack(fill=X)
		self.convertCharWin = Treeview(self.convertTabOptions, columns=("Value"), height=4)
		self.convertCharWin.heading("#0", text="Char")
		self.convertCharWin.heading("Value", text="Value")
		self.convertCharWin.column("#0", width=50)
		self.convertCharWin.column("Value", width=50)
		self.convertCharWin.pack(fill=X)

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
		self.estimateImageInputEntry = Entry(self.estimateTab, textvariable=self.estimateImageInput, width=50)
		self.estimateImageInputEntry.pack(fill=X)
		self.estimateFolderInputEntry = Entry(self.estimateTab, textvariable=self.estimateFolderInput)
		self.estimateFolderInputEntry.pack(fill=X)
		Tooltip.register(self.estimateFolderInputEntry, "Folder with generated chain")
		self.estimateILabel = Label(self.estimateTab)
		self.estimateILabel.pack(fill=X)
		Button(self.estimateTabOptions, text="Load", command=lambda: Thread(target=self.estimateLoad).start(), width=20).pack(fill=X)
		self.estimateIntensityGridEntry = Entry(self.estimateTabOptions, textvariable=self.intensityGridSize)
		self.estimateIntensityGridEntry.pack(fill=X)
		Tooltip.register(self.estimateIntensityGridEntry, "Intensity grid size.")
		self.estimateCharWin = Treeview(self.estimateTabOptions, columns=("Value"), height=3)
		self.estimateCharWin.heading("#0", text="Param")
		self.estimateCharWin.heading("Value", text="Value")
		self.estimateCharWin.column("#0", width=50)
		self.estimateCharWin.column("Value", width=50)
		self.estimateCharWin.pack(fill=X)
		self.estimateIntWin = Treeview(self.estimateTabOptions, columns=(), height=1)
		self.estimateIntWin.heading("#0", text="Intensity")
		self.estimateIntWin.column("#0", width=50)
		self.estimateIntWin.pack(fill=X)
		Button(self.estimateTabOptions, text="Estimate Parameters", command=lambda: Thread(target=self.estimate).start()).pack(fill=X)
		Button(self.estimateTabOptions, text="Copy Parameters", command=lambda: Thread(target=self.copyParameters).start()).pack(fill=X)
		Button(self.estimateTabOptions, text="Stop", command=lambda: Thread(target=self.stop).start()).pack(fill=X)
		self.estimateProgress = Progressbar(self.estimateTabOptions, orient=HORIZONTAL, length=100, mode="indeterminate")
		self.estimateProgress.pack(fill=X, side=BOTTOM)

	def intervalsTabLayout(self):
		self.intervalsTab = Frame(self.notebook)
		self.intervalsTabOptions = Frame(self.intervalsTab)
		self.intervalsTabOptions.pack(side=RIGHT, fill=Y)
		self.notebook.add(self.intervalsTab, text="Intervals")
		self.intervalsImageInput = Entry(self.intervalsTab, textvariable=self.intervalsImage, width=70)
		self.intervalsImageInput.pack(fill=X)
		self.intervalsFolderInput = Entry(self.intervalsTab, textvariable=self.intervalsChain)
		self.intervalsFolderInput.pack(fill=X)
		Tooltip.register(self.intervalsFolderInput, "Folder with generated images from estimated distribution")
		self.intervalsFrame = Frame(self.intervalsTab)
		self.intervalsFrame.pack(fill=X)
		Message(self.intervalsFrame, textvariable=self.aInt, justify=CENTER, relief=RAISED, width=150).pack(side=LEFT, padx=20)
		Message(self.intervalsFrame, textvariable=self.chiInt, justify=CENTER, relief=RAISED, width=150).pack(side=RIGHT, padx=20)
		Message(self.intervalsFrame, textvariable=self.lInt, justify=CENTER, relief=RAISED, width=150).pack()
		self.intervalsILabel = Label(self.intervalsTab)
		self.intervalsILabel.pack(fill=X)
		self.intervalsCharWin = Treeview(self.intervalsTabOptions, columns=("Value"), height=4)
		self.intervalsCharWin.heading("#0", text="Char")
		self.intervalsCharWin.heading("Value", text="Value")
		self.intervalsCharWin.column("#0", width=50)
		self.intervalsCharWin.column("Value", width=50)
		self.intervalsCharWin.pack(fill=X)
		self.intervalsParamWin = Treeview(self.intervalsTabOptions, columns=("Value"), height=4)
		self.intervalsParamWin.heading("#0", text="Param")
		self.intervalsParamWin.heading("Value", text="Value")
		self.intervalsParamWin.column("#0", width=50)
		self.intervalsParamWin.column("Value", width=50)
		self.intervalsParamWin.pack(fill=X)
		Button(self.intervalsTabOptions, text="Load", command=lambda: Thread(target=self.intervalsLoad).start()).pack(fill=X)
		Entry(self.intervalsTabOptions, textvariable=self.intervalsInterval).pack(fill=X)
		Entry(self.intervalsTabOptions, textvariable=self.intervalsChainCount).pack(fill=X)
		Button(self.intervalsTabOptions, text="Summarize", command=lambda: Thread(target=self.summarize).start()).pack(fill=X)

	def preferences(self):
		prefs = Toplevel()
		prefs.title("Preferences")
		Label(prefs, text="General", width=25, font=("Helvetica", 16), anchor=CENTER).pack(fill=X)
		self.updateFreqEntry = Entry(prefs, textvariable=self.updateFreq)
		self.updateFreqEntry.pack()
		Tooltip.register(self.updateFreqEntry, "Update Frequency")
		self.loadingBarIncrementEntry = Entry(prefs, textvariable=self.loadingBarIncrement)
		self.loadingBarIncrementEntry.pack()
		Tooltip.register(self.loadingBarIncrementEntry, "Loading Bar Increment")
		Label(prefs, text="Convert", font=("Helvetica", 16), anchor=CENTER).pack(fill=X)
		self.connectivityEntry = Entry(prefs, textvariable=self.convertConnectivity)
		self.connectivityEntry.pack()
		Tooltip.register(self.connectivityEntry, "Connectivity (only 4 or 8)")
		Label(prefs, text="Simulate", font=("Helvetica", 16), anchor=CENTER).pack(fill=X)
		self.massSimulCountEntry = Entry(prefs, textvariable=self.massSimulCount)
		self.massSimulCountEntry.pack()
		Tooltip.register(self.massSimulCountEntry, "Mass Simulate Count")
		self.chainFolderEntry = Entry(prefs, textvariable=self.chainFolder)
		self.chainFolderEntry.pack()
		Tooltip.register(self.chainFolderEntry, "Mass Simulate folder")
		Label(prefs, text="Estimate", font=("Helvetica", 16), anchor=CENTER).pack(fill=X)
		self.estimateAutoStopEntry = Entry(prefs, textvariable=self.estimateAutoStop)
		self.estimateAutoStopEntry.pack()
		Tooltip.register(self.estimateAutoStopEntry, "Auto Stop (stop when NaN or converged, only 0 or 1)")
		Button(prefs, text="Save Settings", command=lambda: Thread(target=self.saveSettings, args=(2, )).start()).pack(fill=X)

	def variables(self):
		self.updateFreq = IntVar(value=20)
		self.convertInput = StringVar(value=os.path.join("example", "image.png"))
		self.convertThresh = IntVar(value=self.convertDefault["Threshold"])
		self.convertMorphSeq = StringVar(value=self.convertDefault["MorphSeq"])
		self.convertMorphKernel = StringVar(value=self.convertDefault["MorphKernel"])
		self.convertMinCompSize = IntVar(value=self.convertDefault["minCompSize"])
		self.convertMinHoleSize = IntVar(value=self.convertDefault["minHoleSize"])
		self.convertMaxHoleSize = IntVar(value=self.convertDefault["maxHoleSize"])
		self.convertConnectivity = IntVar(value=8)
		self.simulateSize = IntVar(value=self.simulateDefault["Size"])
		self.lambda1 = DoubleVar(value=self.simulateDefault["lambda1"])
		self.lambda2 = DoubleVar(value=self.simulateDefault["lambda2"])
		self.lambda3 = DoubleVar(value=self.simulateDefault["lambda3"])
		self.intensity = DoubleVar(value=self.simulateDefault["Intensity"])
		self.rRange = StringVar(value=self.simulateDefault["rRange"])
		self.simulateIters = IntVar(value=self.simulateDefault["Iterations"])
		self.chainFolder = StringVar(value="chain")
		self.massSimulCount = IntVar(value=19)
		self.estimateImageInput = StringVar(value=os.path.join("example", "image_binaryEdited.png"))
		self.estimateFolderInput = StringVar(value=os.path.join("example", "chain"))
		self.loadingBarIncrement = IntVar(value=5)
		self.estimateAutoStop = BooleanVar(value=1)
		self.convertDisplayed = StringVar()
		self.intervalsImage = StringVar(value=self.convertInput.get())
		self.intervalsChain = StringVar(value=self.chainFolder.get())
		self.intervalsInterval = IntVar(value=90)
		self.intervalsChainCount = IntVar(value=19)
		self.aInt = StringVar(value="A")
		self.lInt = StringVar(value="L")
		self.chiInt = StringVar(value="Chi")
		self.intensityGridSize = IntVar(value=3)
		self.loadSettings(1)
		self.loadSettings(2)

	def bindings(self):
		self.convertDisplayed.trace("w", self.convertChangeDisplayed)
		self.notebook.bind("<<NotebookTabChanged>>", self.notebookResize)
		self.master.bind("<Control-s>", lambda e: self.saveAs())
		self.master.bind("<Control-o>", lambda e: self.openFile())
		self.master.bind("<Control-p>", lambda e: self.preferences())
		self.master.bind("<Control-Left>", self.bindChangeTab)
		self.master.bind("<Control-Right>", self.bindChangeTab)
		self.master.bind("<Return>", lambda e: Thread(target=self.bindEnter).start())

	def convert(self):
		image = Image(filename=self.convertInput.get())
		chars = image.computeChars(threshold=self.convertThresh.get(), connectivity=self.convertConnectivity.get(), kernel=eval(self.convertMorphKernel.get()), seq=eval(self.convertMorphSeq.get()), minCompSize=self.convertMinCompSize.get(), maxHoleSize=self.convertMaxHoleSize.get(), minHoleSize=self.convertMinHoleSize.get())
		self.updateConvertCombobox("_binaryEdited.")
		self.displayChars(chars, self.convertCharWin)

	def simulate(self, mass=[False, 0], ):
		if not self.running:
			self.running = True
			params = (self.lambda1.get(), self.lambda2.get(), self.lambda3.get())
			model = MH(size=self.simulateSize.get(), r=eval(self.rRange.get()), params=params, intensity=self.intensity.get(), connectivity=self.convertConnectivity.get())
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
		if not self.running:
			self.estimateLoad()
			self.running = True
			Thread(target=self.loading, args=(self.estimateProgress, )).start()
			image = self.estimateImageInput.get()
			folder = self.estimateFolderInput.get()
			start = time.time()
			alg = MLE(image, folder=folder, connectivity=self.convertConnectivity)
			prev = numpy.copy(alg.theta)
			while not self.stopFlag:
				alg.iteration()
				if self.estimateAutoStop.get():
					if numpy.sum(numpy.abs(prev-alg.theta)) < 0.0001 or numpy.isnan(numpy.sum(alg.theta)):
						break
				if time.time() - start > 1/self.updateFreq.get():
					self.displayParams(alg.theta, self.estimateCharWin)
					start = time.time()
				prev = numpy.copy(alg.theta)
			alg.saveThetas()
			self.estimateIntensity()
			self.running = False
			

	def estimateIntensity(self):
		obj = Intensity(self.estimateImageInput.get(), self.intensityGridSize.get())
		intensity = obj.estimate()
		for i in self.estimateIntWin.get_children():
			self.estimateIntWin.delete(i)
		self.estimateIntWin.insert("", 0, text=str(intensity))

	def summarize(self):
		if not self.running:
			if self.intervalsLoad():
				self.running = True
				obj = Intervals(self.intervalsImage.get(), self.intervalsChain.get(), self.intervalsInterval.get(), self.intervalsChainCount.get())
				ints = obj.count()
				self.aInt.set("A\n" + str(ints["A"]))
				self.lInt.set("L\n" + str(ints["L"]))
				self.chiInt.set("Chi\n" + str(ints["Chi"]))
				with open(os.path.join(getFolder(self.intervalsImage.get()), "confidence.json"), "w") as conf:
					jsonDict = json.dumps(ints, sort_keys=True, indent=4)
					conf.write(jsonDict)
				i = 0
				for name, interval in ints.items():
					obj.draw(interval, obj.jsonChars[i], name)
					i +=1
				intFolder = os.path.join(getFolder(self.intervalsImage.get()), "intervals")
				aImage = cv2.cvtColor(cv2.imread(os.path.join(intFolder, "A.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
				lImage = cv2.cvtColor(cv2.imread(os.path.join(intFolder, "L.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
				chiImage = cv2.cvtColor(cv2.imread(os.path.join(intFolder, "Chi.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
				img = numpy.concatenate((aImage, lImage, chiImage), axis=0)
				self.display(self.intervalsILabel, matrix=img)
				self.running = False

	def display(self, label, **kwargs):
		height = 500
		width = 1000
		filename = kwargs.pop("filename", None)
		tabName = self.getTabName()
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

	def saveSettings(self, mode):
		if mode == 1:
			path = os.path.join(getFolder(self.convertInput.get()), "settings.json")
			convertJsonDict = json.dumps({
				"Threshold": self.convertThresh.get(),
				"MorphKernel": str(self.convertMorphKernel.get()),
				"MorphSeq": str(self.convertMorphSeq.get()),
				"minCompSize": self.convertMinCompSize.get(), 
				"maxHoleSize": self.convertMaxHoleSize.get(),
				"minHoleSize": self.convertMinHoleSize.get()
				}, sort_keys=True, indent=4)
			with open(path, "w") as settings:
				settings.write(convertJsonDict)
		if mode == 2:
			globalJsonDict = json.dumps({
				"chainFolder": self.chainFolder.get(),
				"massSimulCount": self.massSimulCount.get(),
				"updateFreq": self.updateFreq.get(),
				"loadingBarIncrement": self.loadingBarIncrement.get(),
				"connectivity": self.convertConnectivity.get(),
				"estimateAutoStop": self.estimateAutoStop.get()
				}, sort_keys=True, indent=4)
			with open(self.preferencesFile, "w") as settings:
				settings.write(globalJsonDict)

	def loadSettings(self, mode):
		if mode == 1:
			convertSettingsPath = os.path.join(getFolder(self.convertInput.get()), "settings.json")
			if os.path.exists(convertSettingsPath):
				with open(convertSettingsPath, "r") as settings:
					jsonDict = json.loads(settings.read())
				self.convertThresh.set(jsonDict["Threshold"])
				self.convertMorphSeq.set(jsonDict["MorphSeq"])
				self.convertMorphKernel.set(jsonDict["MorphKernel"])
				self.convertMinCompSize.set(jsonDict["minCompSize"])
				self.convertMinHoleSize.set(jsonDict["minHoleSize"])
				self.convertMaxHoleSize.set(jsonDict["maxHoleSize"])
		if mode == 2:
			if os.path.exists(self.preferencesFile):
				with open(self.preferencesFile, "r") as settings:
					jsonDict = json.loads(settings.read())
				self.chainFolder.set(jsonDict["chainFolder"])
				self.massSimulCount.set(jsonDict["massSimulCount"])
				self.updateFreq.set(jsonDict["updateFreq"])
				self.loadingBarIncrement.set(jsonDict["loadingBarIncrement"])
				self.convertConnectivity.set(jsonDict["connectivity"])
				self.estimateAutoStop.set(jsonDict["estimateAutoStop"])

	def convertLoad(self):
		self.updateConvertCombobox("", True)
		self.loadSettings(1)

	def estimateLoad(self):
		self.running = True
		Thread(target=self.loading, args=(self.estimateProgress, )).start()
		with open(os.path.join(*self.estimateFolderInput.get().split(os.sep), "characteristics.json"), "r") as chars:
			chain = json.loads(chars.read())
		self.displayParams(chain["params"], self.estimateCharWin)
		self.display(self.estimateILabel, filename=self.estimateImageInput.get())
		self.running = False

	def intervalsLoad(self):
		ok = self.intervalsCheck()
		if ok:
			imageFolder = getFolder(self.intervalsImage.get())
			with open(os.path.join(imageFolder, "stats.json"), "r") as chars:
				jsonChars = json.loads(chars.read())
			with open(os.path.join(imageFolder, "estimation.json"), "r") as params:
				jsonParams = json.loads(params.read())
			with open(os.path.join(imageFolder, "intensity.json"), "r") as params:
				intensity = json.loads(params.read())["intensity"]
			paramsIndex = max([int(i) for i in jsonParams.keys()])
			chars = jsonChars["Characteristics"]
			self.displayParams(jsonParams[str(paramsIndex)], self.intervalsParamWin)
			self.displayChars(chars, self.intervalsCharWin)
			self.intervalsParamWin.insert("", 0, text="Intensity", values=(round(intensity, 2)))
		return ok

	def intervalsCheck(self):
		imageFolder = getFolder(self.intervalsImage.get())
		statsExists = os.path.exists(os.path.join(imageFolder, "stats.json"))
		estimationExists = os.path.exists(os.path.join(imageFolder, "estimation.json"))
		intensityExists = os.path.exists(os.path.join(imageFolder, "intensity.json"))
		chainExists = os.path.exists(self.intervalsChain.get())
		if not statsExists:
			messagebox.showerror(title="Error", message="Converted data not found.")
			return False
		if not estimationExists:
			messagebox.showerror(title="Error", message="Estimation data not found.")
			return False
		if not intensityExists:
			messagebox.showerror(title="Error", message="Estimation of intensity not found.")
			return False
		if not chainExists:
			messagebox.showerror(title="Error", message="Chain folder not found.")
			return False
		items = list(os.walk(self.intervalsChain.get()))[0]
		images = [file for folder in items for file in folder if ".png" in file]
		if len(images) < self.intervalsChainCount.get():
			messagebox.showerror(title="Error", message="Not enough chain images.")
			return False
		return True

	def openFile(self):
		tab = self.getTabName()
		if tab == "Simulate":
			messagebox.showerror(title="Error", message="You can't use that in this tab.")
			return
		title = "Choose an image"
		filetypes = (("Image", ".jpg .jpeg .png .bmp"), ("All Files","*.*"))
		path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=filetypes, title=title)
		if path:
			if tab == "Convert":
				self.convertInput.set(path)
				self.display(self.convertILabel, filename=path)
			if tab == "Estimate":
				self.estimateImageInput.set(path)
				self.display(self.estimateILabel, filename=path)
			if tab == "Intervals":
				self.intervalsImage.set(path)
				self.intervalsLoad()

	def openFolder(self):
		tab = self.getTabName()
		if tab in ["Convert", "Simulate"]:
			messagebox.showerror(title="Error", message="You can't use that in this tab.")
			return
		title = "Choose a folder"
		path = filedialog.askdirectory(initialdir=os.getcwd())
		if path:
			if tab == "Estimate":
				self.estimateFolderInput.set(path)
			if tab == "Intervals":
				self.intervalsChain.set(path)

	def saveAs(self):
		tab = self.getTabName()
		if tab != "Simulate":
			messagebox.showerror(title="Error", message="You can't use that in this tab.")
			return
		title = "Choose a location"
		filetypes = (("Image", ".png"), ("All Files", "*.*"))
		path = filedialog.asksaveasfile(initialdir=os.getcwd(), title=title, filetypes=filetypes)
		if path:
			self.tempImage.save(path.name)

	def notebookResize(self, event=None):
		self.notebook.update_idletasks()
		tab = self.notebook.nametowidget(self.notebook.select())
		self.notebook.configure(height=tab.winfo_reqheight(), width=tab.winfo_reqwidth())

	def updateConvertCombobox(self, appendix, load=False):
		items = list(os.walk(getFolder(self.convertInput.get())))[0]
		images = [file for folder in items for file in folder if ".png" in file or ".jpg" in file or ".jpeg" in file or ".bmp" in file or ".tiff" in file]
		self.convertImageChooser["values"] = images
		index = [images.index(item) for item in images if appendix in item][0]
		if load:
			index = images.index(min(images, key=len))
		self.convertDisplayed.set(images[index])

	def convertChangeDisplayed(self, *args):
		path = os.path.join(getFolder(self.convertInput.get()), self.convertDisplayed.get())
		self.display(self.convertILabel, filename=path)

	def copyParameters(self):
		params = list()
		for child in self.estimateCharWin.get_children():
			params.append(float(self.estimateCharWin.item(child)["values"][0]))
		for child in self.estimateIntWin.get_children():
			params.append(float(self.estimateIntWin.item(child)["text"]))
		self.lambda1.set(params[0])
		self.lambda2.set(params[1])
		self.lambda3.set(params[2])
		self.intensity.set(params[3])

	def bindEnter(self):
		tab = self.getTabName()
		if tab == "Convert":
			self.convert()
		elif tab == "Simulate":
			self.simulate()
		elif tab == "Estimate":
			self.estimate()
		elif tab == "Intervals":
			self.summarize()

	def bindChangeTab(self, event):
		tabs = [self.notebook.tab(tab, option="text") for tab in self.notebook.tabs()]
		key = event.keysym
		currentIndex = tabs.index(self.getTabName())
		if key == "Right":
			index = (currentIndex + 1)%len(tabs)
		else:
			if currentIndex == 0:
				index = len(tabs) - 1
			else:
				index = currentIndex - 1
		self.notebook.select(index)
		self.notebookResize()

	def stop(self):
		self.stopFlag = True
		time.sleep(1)
		self.stopFlag = False

	def getTabName(self):
		return self.notebook.tab(self.notebook.nametowidget(self.notebook.select()))["text"]

	def loading(self, bar):
		while self.running:
			bar["value"] += self.loadingBarIncrement.get()
			time.sleep(.05)
		bar["value"] = 0

def getFolder(file):
	return os.sep.join(file.split(os.sep)[:-1])
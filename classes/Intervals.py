import json
import os
import numpy
import statsmodels.stats.api as sms
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class Intervals:
	def __init__(self, image, chain, perc, n):
		self.image = image
		self.chainFolder = chain
		self.perc = perc
		self.n = n
		self.jsonChars, self.jsonChain = self.getData()
		matplotlib.use("agg")

	def count(self):
		a = list()
		l = list()
		chi = list()
		for i in range(self.n):
			a.append(self.jsonChain[str(i+1)][0])
			l.append(self.jsonChain[str(i+1)][1])
			chi.append(self.jsonChain[str(i+1)][2][0]-self.jsonChain[str(i+1)][2][1])
		a = numpy.array(a)
		l = numpy.array(l)
		chi = numpy.array(chi)
		aInt = sms.DescrStatsW(a).tconfint_mean(alpha=1-self.perc/100)
		lInt = sms.DescrStatsW(l).tconfint_mean(alpha=1-self.perc/100)
		chiInt = sms.DescrStatsW(chi).tconfint_mean(alpha=1-self.perc/100)
		intDict = {
				"A": (round(aInt[0], 2), round(aInt[1], 2)),
				"L": (round(lInt[0], 2), round(lInt[1], 2)),
				"Chi": (round(chiInt[0], 2), round(chiInt[1], 2))
				}
		return intDict

	def draw(self, ab, point, name):
		length = ab[1] - ab[0]
		start = numpy.floor(ab[0] - length/10) if point > ab[0] else numpy.floor(point - length/10)
		end = numpy.ceil(ab[1] + length/10) if point < ab[1] else numpy.ceil(point + length/10)
		majorDist = numpy.ceil((end - start)/10)
		minorDist = 0.1 if majorDist <= 1 else 0.5
		figure = plt.figure(figsize=(5, 1))
		ax = plt.subplot(815)
		ax.set_xlim(start, end)
		ax.set_ylim(-5, 5)
		ax.spines["right"].set_color("None")
		ax.spines["left"].set_color("None")
		ax.spines["top"].set_color("None")
		ax.spines["bottom"].set_position("center")
		ax.yaxis.set_major_locator(ticker.NullLocator())
		ax.xaxis.set_major_locator(ticker.MultipleLocator(majorDist))
		ax.xaxis.set_minor_locator(ticker.MultipleLocator(minorDist))
		ax.plot(point, 0, "ro", ms=5, mfc="red")
		ax.axvspan(ab[0], ab[1], color="green", alpha=0.5, ymin=-1, ymax=1)
		ax.text(start, 5, name)
		folder = os.path.join(self.getImageFolder(), "intervals")
		if not os.path.exists(folder): os.mkdir(folder)
		plt.savefig(os.path.join(folder, name + ".png"), transparent=True, dpi=500)
		plt.close()

	def getData(self):
		imageFolder = self.getImageFolder()
		with open(os.path.join(imageFolder, "stats.json"), "r") as chars:
			chars = json.loads(chars.read())["Characteristics"]
			chars[2] = chars[2][0] - chars[2][1]
		with open(os.path.join(self.chainFolder, "characteristics.json"), "r") as chain:
			jsonChain = json.loads(chain.read())
		return chars, jsonChain

	def getImageFolder(self):
		return os.sep.join(self.image.split(os.sep)[:-1])
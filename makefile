all: build clean

clean: clean-files clean-folders

clean-folders:
	find . -name "__pycache__" -exec rm --recursive --force {} +
	find . -name "intervals" -exec rm --recursive --force {} +
	rm --recursive --force chain
	rm --recursive --force dist
	rm --recursive --force build

clean-files:
	find . -name "*_threshold*" -exec rm --force {} +
	find . -name "*_binary*" -exec rm --force {} +
	find . -name "*_intensityGrid*" -exec rm --force {} +
	find . -name "stats.json" -exec rm --force {} +
	find . -name "estimation.json" -exec rm --force {} +
	find . -name "confidence.json" -exec rm --force {} +
	find . -name "intensity.json" -exec rm --force {} +
	rm --force "settings.json"
	
build:
	cp classes/*.py ./
	pyinstaller --onefile gui.spec
	mv dist/statImage ./
	rm --force Gui.py Image.py MH.py MLE.py Tooltip.py Intervals.py Intensity.py

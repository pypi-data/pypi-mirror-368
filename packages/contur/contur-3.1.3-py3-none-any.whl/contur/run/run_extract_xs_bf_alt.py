#!/usr/bin/env python

import os, shutil, sys
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.backends.backend_pdf
from scipy.interpolate import make_interp_spline
import numpy as np
from math import log10, floor
import itertools # for getting pairs from a list
import pandas as pd
import copy
import pickle
from contur.run.arg_utils import setup_common

# set text style in plots to Latex
import shutil
if shutil.which('tex'):
    matplotlib.rcParams['mathtext.fontset'] = 'cm'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
else:
    plt.rcParams['text.usetex'] = False
    plt.rc('font', family='DejaVu Sans')

mergedSigns = True
ignoreXsInitialState = True
mergedJets = True
mergedSChan = True

shortArrow = "->"
arrow = " "+shortArrow+" "
interpretationMap = 	{
				"h1" : "h",
				"h2" : "H",
				"h3" : "A",
				"h4" : "a",
				"h-" : "H-",
				"h+" : "H+",
				"hc" : "H+-",
				"->" : arrow
			}

interpretationMapLatex =	{
					"Z0" : "Z",
					"Xd~" : "\\bar{\\chi}",
					"beta" : "\\beta",
					"tau" : "\\tau",
					"tan" : "\\tan",
					"gamma" : "\\gamma"
				}

interpretationMapLatex_special =	{
					"+" : "^{+}",
					"-" : "^{-}",
					"Xd" : "\\chi",
					"nu_" : "\\nu_",
				}

quarks = ["u", "c", "t", "d", "s", "b"]
jets = ["u", "ubar", "c", "cbar", "d", "dbar", "s", "sbar", "b", "bbar", "g"]

def extractSingleParticle(particles, s, particleType, before=0, after=0):
	pos = s.find(particleType)
	while pos>=0:
		startPos = pos-before
		endPos = pos+len(particleType)+after

		particle = s[startPos:endPos]
		particles.append((particle, pos))
		s = s.replace(particle, "", 1)

		pos = s.find(particleType)

	return s

def getParticlesFromXsec(s):
	particles_and_indices = []

	s = extractSingleParticle(particles_and_indices, s, "bar", before=1)

	for particle in ["d", "u", "c", "s", "b", "gamma", "g"]:
		s = extractSingleParticle(particles_and_indices, s, particle)

	for signedParticle in ["h", "W"]:
		s = extractSingleParticle(particles_and_indices, s, signedParticle, after=1)

	# sort by index
	particles_and_indices.sort(key=lambda val: val[1])
	particles = list(np.array(particles_and_indices)[:,0])

	return particles

class Process():
	def __init__(self, s, particlesOut=None, particlesIntermed=[]):
		self.particlesIntermed = particlesIntermed
		if isinstance(s, list) and isinstance(particlesOut, list):
			self.particlesIn = s
			self.particlesOut = particlesOut

		elif isinstance(s, str):
			if shortArrow in s: # is BR
				inP, outP = s.split(shortArrow)
				self.particlesIn = [inP]
				self.particlesOut = outP.split(",")

			else: # is Xsec
				inP, outP = s.split("2", 1)
				self.particlesIn = getParticlesFromXsec(inP)
				if ignoreXsInitialState:
					for i in range(len(self.particlesIn)):
						self.particlesIn[i] = "p"
				self.particlesOut = getParticlesFromXsec(outP)
				if len(self.particlesOut)>2:
					self.particlesIntermed = [self.particlesOut[0]]
					self.particlesOut = self.particlesOut[1:]

		else:
			raise TypeError("Expect string or two lists for creating a process.")

		for i in range(len(self.particlesIn)):
			self.particlesIn[i] = makeHumanReadable(self.particlesIn[i])
		for i in range(len(self.particlesIntermed)):
			self.particlesIntermed[i] = makeHumanReadable(self.particlesIntermed[i])
		for i in range(len(self.particlesOut)):
			self.particlesOut[i] = makeHumanReadable(self.particlesOut[i])

		# sort lists
		self.particlesIn = sorted(self.particlesIn)
		self.particlesIntermed = sorted(self.particlesIntermed)
		self.particlesOut = sorted(self.particlesOut)

	def __repr__(self):
		if len(self.particlesIntermed)>0:
			return ", ".join(self.particlesIn)+arrow+", ".join(self.particlesIntermed)+arrow+", ".join(self.particlesOut)
		return ", ".join(self.particlesIn)+arrow+", ".join(self.particlesOut)

	def __eq__(self, other):
		# other class
		if not isinstance(other, self.__class__):
			return False

		# different list lengths
		if not len(self.particlesIn)==len(other.particlesIn) or not len(self.particlesIntermed)==len(other.particlesIntermed) or not len(self.particlesOut)==len(other.particlesOut):
			return False

		# match list contents
		for i in range(len(self.particlesIn)):
			if not self.particlesIn[i]==other.particlesIn[i]:
				return False

		for i in range(len(self.particlesIntermed)):
			if not self.particlesIntermed[i]==other.particlesIntermed[i]:
				return False

		for i in range(len(self.particlesOut)):
			if not self.particlesOut[i]==other.particlesOut[i]:
				return False

		return True

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(repr(self))

	def __lt__(self, other):
		return str(self)<str(other)

	def isDecay(self):
		return len(self.particlesIn)==1

	def toLatex(self):
		# copy lists
		latexIn = self.particlesIn[:]
		latexIntermed = self.particlesIntermed[:]
		latexOut = self.particlesOut[:]

		for currList in latexIn, latexIntermed, latexOut:
			for i in range(len(currList)):

				if "bar" in currList[i]:
					currList[i] = "\\bar{%s}" % currList[i].replace("bar", "")
				else:
					currList[i] = makeLatex(currList[i])

		if len(self.particlesIntermed)>0:
			s = "".join(latexIn)+" \\rightarrow "+", ".join(latexIn)+" \\rightarrow "+"".join(latexOut)
		else:
			s = "".join(latexIn)+" \\rightarrow "+"".join(latexOut)

		return s

	def goesTo(self, particle):
		return particle in self.particlesOut

	def comesFrom(self, particle):
		return particle in self.particlesIn

	def sameState(self, other, state):
		if state=="initial":
			particles1 = self.particlesIn
			particles2 = other.particlesIn
		elif state=="final":
			particles1 = self.particlesOut
			particles2 = other.particlesOut
		else:
			raise ValueError("Have to tell whether looking for 'initial' or 'final' state.")

		if not len(particles1)==len(particles2):
			return False
		for i in range(len(particles1)):
			if not particles1[i]==particles2[i]:
				return False
		return True

	def invertSigns(self):
		process = copy.deepcopy(self)

		def replaceSigns(s):
			if "+" in s or "-" in s:
				s = s.replace("+", "MINUS")
				s = s.replace("-", "+")
				s = s.replace("MINUS", "-")

			elif "Xd" in s:
				if s=="Xd":
					s = "Xd~"
				elif s=="Xd~":
					s = "Xd"

			else:
				for jet in quarks:
					if s==jet:
						s = jet+"bar"
					elif s==jet+"bar":
						s = jet
			return s

		for i in range(len(process.particlesIn)):
			process.particlesIn[i] = replaceSigns(process.particlesIn[i])
		for i in range(len(process.particlesIntermed)):
			process.particlesIntermed[i] = replaceSigns(process.particlesIntermed[i])
		for i in range(len(process.particlesOut)):
			process.particlesOut[i] = replaceSigns(process.particlesOut[i])

		return process

	def allParticles(self):
		return self.particlesIn+self.particlesIntermed+self.particlesOut

	def isSigned(self):
		signs = ["+", "-", "~", "bar"]
		for particle in self.allParticles():
			for s in signs:
				if s in particle:
					return True
			for jet in quarks:
				if s == jet:
					return True
		return False

# replace computational symbols with human-readable ones
def makeHumanReadable(s):
	for key, value in interpretationMap.items():
		s = s.replace(key, value)
	return s

# convert special characters in a string to LaTeX code
def makeLatex(s):
	maps = [interpretationMapLatex, interpretationMapLatex_special]
	for m in maps:
		for key, value in m.items():
			s = s.replace(key, value)
	if s.startswith("m"):
		s = "m_{%s}" % s[1:]

	if mergedSigns:
		s = s.replace("+", "\\pm")
		s = s.replace("-", "\\mp")

	return s

# convert string to number by removing uncertainty expression
def stringToNumber(s):
	openBrace = 0
	closeBrace = 0
	for i in range(len(s)):
		if s[i]=="(":
			openBrace = i
		if s[i]==")":
			closeBrace = i
		if openBrace!=0 and closeBrace!=0:
			return s[:openBrace]+s[closeBrace+1:]
	return s

# extract the param values from file
def getParams(fileName, paramNames):
	dic = {}
	with open(fileName, "r") as f:
			lines = f.readlines()
			for line in lines:
				words = line.split(" ")
				paramName = makeHumanReadable(words[0])
				dic[paramName] = float(words[2].strip("\n"))
				paramNames.add(paramName)
	return dic, set(paramNames)

# get the BRs from the file
def getBRs(fileName, brTypes):
	# store one dict for processes and one for BRs for faster comparisons
	dic_proc = {}
	dic_BRs = {}
	with open(fileName, "r") as f:
		lines = f.readlines()

		# find lines that have the keyword "Parent" in them
		linePos = 0
		parentPos = []
		for line in lines:
			if "Parent" in line:
				parentPos.append(linePos)
			linePos += 1

		# get BRs for each parent
		for parent in parentPos:
			linePos = parent+2
			line = lines[linePos]
			while "#" not in line:
				words = [x for x in line.split(" ") if not x==""]
				process = Process(words[0].strip(";"))
				br = float(words[2])

				dic_BRs[str(process)] = br
				dic_proc[str(process)] = process

				# if this process was not known yet: add it
				# it's a set to duplicates are handled automatically
				brTypes.add(process)

				linePos += 1
				line = lines[linePos]
	dic = {}
	for key in dic_BRs:
		dic[dic_proc[key]] = dic_BRs[key]
	return dic, brTypes

# get the Xsecs from the file
def getXsecs(fileName, xsecTypes):
	dic = {}
	with open(fileName, "r") as f:
		lines = f.readlines()

		# find lines that have the keyword "Parent" in them
		for line in lines:
			if not line.startswith("ME"):
				continue

			words = [x for x in line.split(" ") if not x==""]
			process = Process(words[0].strip("ME"))
			xsec = float(stringToNumber(words[3].strip("\n")))
			dic[process] = xsec*1000 # convert nb to fb

			xsecTypes.add(process)
	return dic, xsecTypes

# check whether one parameter is constant over the whole scan
def checkAllEqual(dic, param, storedParam, key=None):
	for row in dic.values():
		if key is None:
			paramValue = row[param]
		else:
			paramValue = row[key][param]
		if paramValue!=storedParam:
			return False
	return True

# check whether one parameter is above a given threshold
def allBelowThreshold(values, key, processType, threshold):
	for item in values.values():
		processDic = item[key]
		if processType in processDic and processDic[processType]>=threshold:
			return False
	return True

# merge signs
def mergeSigns(dic):
	keys_to_skip = [] # make list global so same signs are skipped for all points
	for point in dic.values():
		for key in ["xs", "BRs"]:
			processes = point[key]

			matching_dic = {}
			for process in processes:
				matching_dic[str(process)] = process

			keys = list(processes.keys())

			for process in sorted(keys):
				if not process.isSigned(): # process doesn't have any sign
					continue

				if str(process) in keys_to_skip: # already handled this case
					continue
				inverted_process = str(process.invertSigns())
				if inverted_process in matching_dic:
					processes[process] += processes[matching_dic[inverted_process]] # sum BRs/ xs
					processes.pop(matching_dic[inverted_process]) # remove unneeded process
					keys_to_skip.append(inverted_process)

	return dic

# merge jets in xs
def mergeJets(dic):
	for point in dic.values():
		xsecs = point["xs"]

		matching_dic, new_xsecs = {}, {}

		for process, xs in xsecs.items():
			if process.isDecay(): # don't merge for BRs
				continue

			# replace particles by jets
			for i, particle in enumerate(process.particlesOut):
				if particle in jets:
					process.particlesOut[i] = "j"
				else:
					process.particlesOut[i] = process.particlesOut[i].replace("bar", "") # can ignore bars for this case

			if str(process) in matching_dic:
				new_xsecs[matching_dic[str(process)]] += xs # sum xs
			else:
				matching_dic[str(process)] = process
				new_xsecs[process] = xs

		point["xs"] = new_xsecs
	return dic

# merge jets in xs
def mergeSChan(dic):
	for point in dic.values():
		xsecs = point["xs"]

		matching_dic, new_xsecs = {}, {}

		for process, xs in xsecs.items():
			if process.isDecay(): # don't merge for BRs
				continue

			# replace out-particles by copy of intermediate particle
			if len(process.particlesIntermed)>0:
				process.particlesOut = list(process.particlesIntermed)
				process.particlesIntermed = []

			if str(process) in matching_dic:
				new_xsecs[matching_dic[str(process)]] += xs # sum xs
			else:
				matching_dic[str(process)] = process
				new_xsecs[process] = xs

		point["xs"] = new_xsecs
	return dic

# remove duplicate param values from dictionary
def slimParams(values, paramNames):
	paramNamesToRemove = []
	for param in paramNames: # check each parameter
		storedParam = list(values.values())[0]["params"][param] # first one is default

		if not checkAllEqual(values, param, storedParam, "params"): # if parameter is not constant
			continue

		paramNamesToRemove.append(param) # mark for removal from paramNames; cannot remove now as we're iterating over paramNames
		for row in values:
			values[row]["params"].pop(param) # remove it from dictionary

	# remove unneccessary paramNames
	paramNames = [x for x in paramNames if x not in paramNamesToRemove]

	return values, paramNames

# remove values below threshold from dictionary
def slimValues(values, columnNames, threshold, key):
	columnsToRemove = []
	for columnName in columnNames: # check each BR type
		if not allBelowThreshold(values, key, columnName, threshold): # check if any value is larger than threshold
			continue # this one is fine, continue

		columnsToRemove.append(columnName) # mark for removal from brTypes; cannot remove now as we're iterating over brTypes
		for point in values.values():
			if columnName in point[key]: # remove only if columnName exists for row
				point[key].pop(columnName) # remove it from dictionary

	# remove unneccessary paramNames
	columnNames = [x for x in columnNames if x not in columnsToRemove]

	return values, columnNames

# fill missing entries with zeroes
def fillGaps(values, brTypes, xsecTypes):
	types = brTypes+xsecTypes
	for row in values:
		for currType in types:
			if not currType in values[row]: # entry doesn't exist, set to 0
				values[row][currType] = 0

# get the dictionary
def getDictionary(inputDir, brThresh, xsecThresh):
	print( "Extracting values ...")
	paramNames = set()
	brTypes = set()
	xsecTypes = set()
	values = {}
	gap = "                   "
	for root, dirs, files in os.walk(inputDir):
		row = {}
		for f in files:
			filePath = os.path.join(root, f)
			if f=="params.dat": # is a parameters file
				row["params"], paramNames = getParams(filePath, paramNames)

			if "herwig-S" in f and f.endswith("log") and not "EvtGen" in f: # is a logfile with BRs
				row["BRs"], brTypes = getBRs(filePath, brTypes)

			elif "herwig-S" in f and f.endswith("out"): # is an outfile with Xsecs
				row["xs"], xsecTypes = getXsecs(filePath, xsecTypes)
		if row:
			values[root] = row


	# merge s-channel
	if mergedSChan:
		print("Merging s-channel ...")
		values = mergeSChan(values)

	# merge signs if requested
	if mergedSigns:
		print("Merging signs ...")
		values = mergeSigns(values)

	# merge jets if requested
	if mergedJets:
		print("Merging jets ...")
		values = mergeJets(values)

	# remove unnecessary columns
	print("Slimming dictionary ...")
	values, paramNames = slimParams(values, paramNames)
	values, brTypes = slimValues(values, brTypes, brThresh, "BRs")
	values, xsecTypes = slimValues(values, xsecTypes, xsecThresh, "xs")

	# sort brTypes and xsecTypes
	brTypes = sorted(brTypes)
	xsecTypes = sorted(xsecTypes)

	fieldNames = paramNames+[gap]+brTypes+[gap]+xsecTypes
	return values, paramNames, brTypes, xsecTypes, fieldNames

# write the dictionary into a csv file
def writeToCSV(values, fieldNames, outputFile):
	print("Writing to csv ...")
	import csv
	with open(outputFile, "w") as csvFile:
		csvWriter = csv.DictWriter(csvFile, fieldnames=fieldNames, delimiter='\t')

		csvWriter.writeheader()
		for row in values:
			csvWriter.writerow(values[row])

# save plots
def savePlots(plots, outDir, title):
	pdfPath = os.path.join(outDir, title)+".pdf"
	pdf = matplotlib.backends.backend_pdf.PdfPages(pdfPath)
	for fig in plots:
		pdf.savefig(plots[fig])
	pdf.close()
	plt.close("all")

# get decaying particle from whole decay process
def getDecayingParticle(brType):
	return brType[:brType.find(arrow)]

# prepare the dictionary with the data
def prepareDataGrid(processGroups, processTypes):
	data = {}
	for processGroup in processGroups: # processGroup is either a decaying particle or "xsec"
		data[processGroup] = {}
		for processType in processTypes:
			condition = (processType.particlesIn[0]+"_BR"==processGroup)
			for outParticle in processType.particlesOut:
				condition = (condition or processGroup==outParticle+"_xsec")

			if not condition:
				continue

			# for x- and y-coordinates
			data[processGroup][str(processType)+"X"] = []
			data[processGroup][str(processType)+"Y"] = []

	return data

# round number to given significant digits
def roundedString(x, precision=3):
	x = float(x)
	return str(round(x, -int(floor(log10(abs(float(x)))))+precision-1))

def enableLatex():
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif')

# save slices of dictionary as plots
def saveAsPlots(values, paramNames, brTypes, xsecTypes, outDir, smooth=False, xlog=False, ylog=False, brThreshold=None):
	print("Saving as plots ...")

	processGroups = {}
	for brType in brTypes:
		decayingParticle = brType.particlesIn[0]+"_BR"
		if decayingParticle not in processGroups:
			processGroups[decayingParticle] = []
		processGroups[decayingParticle].append(brType)

	finalStateParticles = ["u", "ubar", "d", "dbar", "c", "cbar", "s", "sbar", "b", "bbar", "t", "tbar", "g", "H+"]
	interestingParticles = ["h", "H", "a", "A", "H+", "H-"]
	for fsp in finalStateParticles:
		processGroups[fsp+"_xsec"] = []
		for xsecType in xsecTypes:
			try:
				indexJet = xsecType.particlesOut.index(fsp)
				indexOther = abs(indexJet-1)
				if xsecType.particlesOut[indexOther] in interestingParticles:
					processGroups[fsp+"_xsec"].append(xsecType)
			except:
				continue
	processTypes = brTypes + xsecTypes

	axes = getAxes(values, paramNames)

	for fixedParamName in paramNames: # loop horizontal and vertical
		constStr = "%s=const." % fixedParamName
		print("\nSaving plots for %s" % constStr)

		currOutDir = os.path.join(outDir, constStr)
		os.makedirs(currOutDir)

		variableParamName = [x for x in paramNames if x!=fixedParamName][0]

		# get grid points
		fixedParamValues = axes[fixedParamName]

		# loop over slices
		for fixedParam in fixedParamValues:
			figures = {}

			data = prepareDataGrid(processGroups, processTypes)

			# fill grid
			for point in values.values(): # loop over entries
				if point["params"][fixedParamName]!=fixedParam: # this is not a row that has to be drawn
					continue

				x = point["params"][variableParamName]
				for brType in brTypes:
					if brType not in point["BRs"]: # handle only if key exists
						continue
					y = point["BRs"][brType]

					initialState = brType.particlesIn[0]+"_BR"
					data[initialState][str(brType)+"X"].append(float(x))
					data[initialState][str(brType)+"Y"].append(float(y))

				for xsecType in xsecTypes:
					if xsecType not in point["xs"]: # handle only if key exists
						continue

					y = point["xs"][xsecType]
					for outParticle in xsecType.particlesOut:
						finalState = outParticle+"_xsec"
						if finalState not in data:
							continue
						data[finalState][str(xsecType)+"X"].append(float(x))
						data[finalState][str(xsecType)+"Y"].append(float(y))

			# fill plots
			# loop over figures and assign data points
			for processGroup in processGroups:
				# create plot
				fig = plt.figure()

				# fill plots
				for processType in processGroups[processGroup]:
					xPoints = data[processGroup][str(processType)+"X"]
					yPoints = data[processGroup][str(processType)+"Y"]

					if len(xPoints)==0: # didn't find points
						continue

					# sort points
					xPoints, yPoints = zip(*sorted(zip(xPoints, yPoints)))

					# smooth curves if necessary
					if smooth:
						xPoints_smooth = np.linspace(xPoints[0], xPoints[-1], 300) #300 represents number of points to make between xmin and xmax
						spl = make_interp_spline(xPoints, yPoints)
						yPoints = spl(xPoints_smooth)
						xPoints = xPoints_smooth

					plt.plot(xPoints, yPoints, label="$%s$" % processType.toLatex())

				figuresTitle = "$%s=%s$" % (makeLatex(fixedParamName), roundedString(fixedParam))
				if figuresTitle.startswith("$m"):
					figuresTitle += " GeV"

				processGroupTitle, processGroupType = processGroup.split("_")
				yLabel = processGroupType
				if processGroupType=="xsec":
					yLabel = "$\sigma$ / nb"
					selProcess = Process(["p", "p"], [processGroupTitle, "X"])
					fig.suptitle("%s, $\sigma_{%s}$" % (figuresTitle, selProcess.toLatex()))

					plt.yscale("log")

				elif processGroupType=="BR":
					fig.suptitle("%s, %ss($%s$)" % (figuresTitle, yLabel, makeLatex(processGroupTitle)))

					if ylog:
						plt.yscale("log")
						yMin = pow(10,-3)
						if brThreshold:
							yMin = brThreshold
						plt.ylim(yMin, 1.02)
					else:
						plt.ylim(-0.02, 1.02)

				plt.xlabel(makeLabel(variableParamName))
				plt.ylabel(yLabel)
				plt.legend()
				plt.grid(axis="y")

				if xlog:
					plt.xscale("log")

				# add to figures
				figures[processGroup] = fig

			print("Saving %s=%s" % (fixedParamName, roundedString(fixedParam)))
			savePlots(figures, currOutDir, fixedParamName+"="+roundedString(fixedParam))

def getAxes(dic, paramNames):
	axes = {}
	for paramName in paramNames:
		axes[paramName] = set()
		for point in dic.values(): # loop over entries
				value = point["params"][paramName]
				if value not in axes[paramName]:
						axes[paramName].add(value)

		axes[paramName] = sorted(axes[paramName])
	return axes

def getSmallestNumberAbove(grid, limit):
	minimum = sys.float_info.max
	for x in grid.flat:
		if x>limit and x<minimum:
			minimum = x
	return minimum

# shorten a float such that it's suitable for a label
def toScientific(number):
	return "{:0.1e}".format(number)

# compute the label position from to sequential bins
def getLabelPos(axis, i):
	return axis[i]+(axis[i+1]-axis[i])/2

# show the bin contents as text
def induceGrid(xAxis, yAxis, z):
	for i in range(len(xAxis)-1):
		x = getLabelPos(xAxis, i)
		for j in range(len(yAxis)-1):
			y = getLabelPos(yAxis, j)
		plt.text(x, y, toScientific(z[i,j]), color="w", ha="center", va="center", fontsize="4")

# draw a 2D plot
def plot2D(x, y, z, xlog=False, ylog=False, zlog=False, title="", xlabel="", ylabel="", zlabel=None):
	fig, ax0 = plt.subplots()
	if zlog:
		im = ax0.pcolormesh(x, y, z.T, norm=colors.LogNorm(vmin=getSmallestNumberAbove(z, 0), vmax=z.max()), shading="auto")
	else:
		im = ax0.pcolormesh(x, y, z.T, shading="auto")
	if zlabel==None:
		zlabel=title
	fig.colorbar(im, ax=ax0, label=zlabel)
	plt.suptitle(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)

	if xlog:
		plt.xscale("log")
	if ylog:
		plt.yscale("log")

	induceGrid(x, y, z)

	return fig

# convert given string into a something suitable for an axis label
def makeLabel(name):
	name = "$%s$" % makeLatex(name)
	if name.startswith("$m"): # is a mass
		name += " / GeV"
	return name

def create2Dplots(values, paramNames, xsecTypes, outDir, xlog=False, ylog=False, zlog=False):
	print("Saving 2D plots ...")

	xName = paramNames[0]
	yName = paramNames[1]
	axes = getAxes(values, paramNames)
	xAxis = axes[xName]
	yAxis = axes[yName]
	z = {}
	figures = {}
	selections = {}

	for selection in [["H+", "H-"], ["H+", "tbar"]]:
		selProcess = Process(["p", "p"], selection)
		selections[selProcess] = selProcess
		z[selProcess] = np.zeros((len(xAxis), len(yAxis)), dtype=float)

		for process in xsecTypes:
			if process.isDecay():
				continue

			if not process.sameState(selProcess, "final"):
				continue

			for point in values.values():
				x = xAxis.index(point["params"][xName])
				y = yAxis.index(point["params"][yName])

				z[selProcess][x][y] = point["xs"][process]

		title="$\sigma_{%s}$" % selProcess.toLatex()
		figures[selProcess] = plot2D(xAxis, yAxis, z[selProcess], xlog=xlog, ylog=ylog, zlog=zlog, title=title, xlabel=makeLabel(xName), ylabel=makeLabel(yName), zlabel="%s / nb" % title)

	# ratio plots
	for pair in itertools.combinations(selections, 2):
		z_ratio = z[pair[0]] / z[pair[1]]
		title = "$\sigma_{%s} / \sigma_{%s}$" % (pair[0].toLatex(), pair[1].toLatex())
		figures[pair] = plot2D(xAxis, yAxis, z_ratio, xlog=xlog, ylog=ylog, zlog=zlog, title=title, xlabel=makeLabel(xName), ylabel=makeLabel(yName))

	savePlots(figures, outDir, "Xsecs_hc")

def getGrid(dic, paramNames):

	data = {
		"xs" : {},
		"BRs" : {}
	}

	#jets = ["u", "ubar", "d", "dbar", "c", "cbar", "s", "sbar", "b", "bbar", "t", "tbar", "g", "H+"]
	#interestingParticles = ["h", "H", "a", "A", "H+", "H-"]
	#for jet in jets:
	#	data["xs"][jet] = {}
	#	for xsecType in xsecTypes:
	#		if jet in xsecType.particlesOut:
	#			indexJet = xsecType.particlesOut.index(jet)
	#			indexOther = abs(indexJet-1)
	#			if xsecType.particlesOut[indexOther] in interestingParticles:
	#				data["xs"][jet][xsecType] = []

	axes = getAxes(dic, paramNames)
	axes_keys = list(axes.keys())

	def get_dataframe(axes):
		keys = list(axes.keys())
		return pd.DataFrame(columns=axes[keys[0]], index=axes[keys[1]])

	interesting_categories = {
		"BRs" : ["H", "a", "A", "H+", "H-"],
		"xs" : ["H", "a", "A", "H+", "H-"],
	}

	for key, processDic in data.items():
		for point in dic.values():
			for process, val in point[key].items():
				category = None
				if key == "BRs":
					category = process.particlesIn[0]
					if category not in interesting_categories[key]:
						continue
				elif key == "xs":
					if len(process.particlesIntermed)==0:
						currParticles = process.particlesOut
					else:
						currParticles = process.particlesIntermed
					for particle in currParticles:
						if particle in interesting_categories[key]:
							category = particle
							break

					if category is None: # not interesting
						continue
				else:
					raise Exception(f"Key {key} not recognised.")

				if category not in processDic:
					processDic[category] = {}

				# check if key already available
				found = False
				processInDict = None
				for currProcess in processDic[category]:
					if str(currProcess)==str(process) and currProcess!=process:
						print("Not equal: ", currProcess, process)
					if currProcess==process:
						found = True
						processInDict = currProcess
						break
				if not found:
					processInDict = process
					processDic[category][processInDict] = get_dataframe(axes)

				x = point["params"][axes_keys[0]]
				y = point["params"][axes_keys[1]]

				processDic[category][processInDict].at[y,x] = val

	return data, axes

def drawGrid(grid, axes_info, outDir=""):
	axes_info_keys = list(axes_info.keys())
	max_rows = 4
	xVals = axes_info[axes_info_keys[0]]
	yVals = axes_info[axes_info_keys[1]]
	nrows = min(max_rows, len(yVals))

	if axes_info_keys[1]=="tanbeta":
		axes_info_keys[1] = "tb"
	elif axes_info_keys[1]=="mXd":
		axes_info_keys[1] = "mX"
	axes_dic = {"x_label" : axes_info_keys[0], "y_label": axes_info_keys[1]}


	yValsPlot = []
	if nrows==4:
		if axes_dic["y_label"]=="mA":
			yValsPlot = [yVals[1], yVals[2], yVals[4], yVals[8]]
		elif axes_dic["y_label"]=="tb":
			yValsPlot = [yVals[3], yVals[5], yVals[10], yVals[-2]]
		elif axes_dic["y_label"]=="mX":
			yValsPlot = [yVals[1], yVals[2], yVals[4], yVals[10]]
	if not yValsPlot:
		ratio = float(len(yVals))/nrows
		sum = 0
		while sum < len(yVals):
			yValsPlot.append(yVals[int(sum)])
			sum += ratio

	for processType, processDic in grid.items(): # loop over BRs and xs
		for category, categoryDic in processDic.items():
			fig, axes = plt.subplots(nrows=nrows, sharex=True)
			plt.subplots_adjust(hspace=0)

			legendLabels = []
			legendHandles = []
			colorDic = {}
			colorsTaken = []

			axes[-1].set_xlabel(axes_dic["x_label"], fontsize="x-large")
			for i, yVal in enumerate(yValsPlot):
				ax = axes[nrows-1-i]

				# get maximum cross section for this plot
				if processType=="xs":
					xsMax = -1
					for process, processMatrix in categoryDic.items():
						xsMax = max(xsMax, max(processMatrix.loc[yVal]))
					xsCutOff = xsMax*0.0015

				for process, processMatrix in categoryDic.items():
					xValsThisPlot = list(xVals)
					yValsThisPlot = list(processMatrix.loc[yVal])
					# skip values below threshold:
					if processType=="xs":
						if max(yValsThisPlot)<xsCutOff:
							continue
					elif processType=="BRs":
						if max(yValsThisPlot)<0.05:
							continue

					# drop zeros for xs
					if processType=="xs":
						toRemove = []
						for i in range(len(yValsThisPlot)):
							if yValsThisPlot[i]==0:
								toRemove.append(i)

						for i in sorted(toRemove, reverse=True):
							del xValsThisPlot[i]
							del yValsThisPlot[i]

						# skip entries with only one or fewer points
						if np.count_nonzero(yValsThisPlot)<=1:
							continue

					kwargs = {}
					if str(process) in colorDic: # colour exists
						kwargs["color"] = colorDic[str(process)]

					handle = ax.plot(xValsThisPlot, yValsThisPlot, linewidth=4, **kwargs)
					if str(process) not in colorDic:
						legendLabels.append(f"${process.toLatex()}$")
						legendHandles.append(handle[0])
						color = handle[0].get_color()
						colorDic[str(process)] = color
						colorsTaken.append(color)

				if processType == "BRs":
					ax.set_ylim([0.01, 1.01])
				else:
					ax.set_yscale("log")
					ylim = ax.get_ylim()
					ax.set_ylim([xsCutOff, ylim[1]*0.99])
				ax.yaxis.tick_right()
				ax.tick_params("y", which="both", left=True)

				# y_label
				precision = 0.1
				digits = max(0, -int(np.log10(precision)))
				ylabel = "{:.{:}f}".format(roundToPrecision(yVal, precision), digits)
				ax.set_ylabel(ylabel, fontsize="x-large")

			axes[-1].set_xlim([min(xVals), max(xVals)])

			ymin_legend = 0.89-(nrows-3)*0.005
			xmin_plotInfo = 0.16
			fig.text(xmin_plotInfo, ymin_legend+0.058, "Herwig generation")
			fig.legend(handles=legendHandles, labels=legendLabels, frameon=False, loc="lower left", bbox_to_anchor=(0.33, ymin_legend), ncol=3)
			fig.text(0.06, 0.54, axes_dic["y_label"], fontsize="x-large", rotation=90, va="center")

			yLabelLarge = ""
			yLabelLargePos = 0.5
			if processType=="BRs":
				yLabelLarge = r"$\mathcal{B}_f("+makeLatex(category)+")$"
			else:
				yLabelLarge = r"$\sigma_{pp\rightarrow "+makeLatex(category)+"X}$ [fb]"
				yLabelLargePos = 0.45
			fig.text(1.01, yLabelLargePos, yLabelLarge, fontsize="x-large", rotation=90)

			savePrefix = "BR" if processType=="BRs" else processType
			saveName = f"{os.path.join(outDir, savePrefix+'_'+category)}"
			plt.savefig(saveName)
			print(f"Saved as {saveName}")

def roundToPrecision(yVal, precision):
	return round(yVal/precision)*precision


def main(args):
	setup_common(args)

	if not args["csv"] and not args["plots"] and not args["plot2D"]:
		print("Nothing to do.")
		exit()

	if not os.path.isdir(args["inputDirectory"]):
		raise Exception(f"Directory {args['inputDirectory']} does not exist.")

	if os.path.isdir(args["outDir"]): # remove directory if existing
		shutil.rmtree(args["outDir"])
	os.makedirs(args["outDir"])

	fileName = "temp.pickle"
	if os.path.isfile(fileName):
		print(f"Reading file {fileName}...")
		with open(fileName, "rb") as f:
			grid, axes, values, paramNames, brTypes, xsecTypes = pickle.load(f)
	else:
		values, paramNames, brTypes, xsecTypes, fieldNames = getDictionary(args["inputDirectory"], args["BRthreshold"], args["XSECthreshold"])
		paramNames = [makeHumanReadable(args["param1"]), makeHumanReadable(args["param2"])]
		grid, axes = getGrid(values, paramNames)
		with open(fileName, "wb") as f:
			pickle.dump([grid, axes, values, paramNames, brTypes, xsecTypes], f)

	if args["csv"]:
		outputCSV = os.path.join(args["outDir"], "xsecBR.csv")
		writeToCSV(values, fieldNames, outputCSV)

	if args["plots"]:
		if args["slices"]:
			saveAsPlots(values, paramNames, brTypes, xsecTypes, args["outDir"], smooth=args["smooth"], xlog=args["xlog"], ylog=args["ylog"], brThreshold=args["BRthreshold"])
		else:
			drawGrid(grid, axes, outDir=args["outDir"])

	if args["plot2D"]:
		create2Dplots(values, paramNames, xsecTypes, args["outDir"], xlog=args["xlog"], ylog=args["ylog"], zlog=args["zlog"])

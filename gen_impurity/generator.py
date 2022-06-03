import os, sys
import shutil
import subprocess
from time import time, sleep

import numpy as np

from lib.input import Input

class MainLoop:
    def __init__(self):
        # env variables
        self.cpuNumber = 12                 #number of cores
        self.rootDir = os.getcwd()          #present directory
        self.folderHeader = "Run_"          #name of FLUKA working space
        self.inpName_FLUKA = "run"          #input name of FLUKA
        self.flukaDir = "fluka"             #folder that contains original FLUKA input
        self.outputDir = "output"           #folder that save all outputs of FLUKA calculation
        self.outputHeader = "res"           #filename header of output file

        # do not change
        self.numPreResult = 0              
        self.isFirst = np.ones(self.cpuNumber, dtype=bool)

        self._inp = Input(os.path.join(self.rootDir, self.flukaDir, self.inpName_FLUKA + ".inp"))

        #initialization
        self._GetTargetExt("settings/ext_filter.txt")
        self._GetBashCommand("settings/command.txt")
        self._FolderGen()
        self._SearchLastHistories()

        self.process = []
        for i in range(self.cpuNumber):
            self.process += [subprocess.Popen([sys.executable,
                                               "lib/pinitializer.py"],
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE)]

    def Execute(self):
        #execute the mainloop
        while True:
            for i in range(self.cpuNumber):
                if self.process[i].poll() is 0:
                    if self.isFirst[i]:
                        self.isFirst[i] = False
                    else:
                        self._CpyResult(i)
                    self._randomInpGen(i)
                    self._run(i)
            sleep(1)

    def _GetTargetExt(self, fileName):
        #get target file extension
        self.targetExt = []
        file = open(fileName)
        lines = file.readlines()
        for line in lines:
            if line[0] != "*":
                self.targetExt += [line.split()[0]]
        file.close()

    def _GetBashCommand(self, fileName):
        #get bash command line
        fileCom = open(fileName)
        self.bashCmd = fileCom.readlines()[0][:-1]
        fileCom.close()

    def _FolderGen(self):
        #generate fluka running folders
        #and copy the input and executable file
        folders = os.listdir(self.rootDir)
        if self.outputDir not in folders:
            os.mkdir(os.path.join(self.rootDir, self.outputDir))
            print("Folder " + self.outputDir + " is generated")
        for i in range(self.cpuNumber):
            folderName = self.folderHeader + str(i)
            if folderName in folders:
                shutil.rmtree(os.path.join(self.rootDir, folderName))
            os.mkdir(os.path.join(self.rootDir, folderName))
            print("Folder " + folderName + " is generated")
        print("===========================================================")

    def _SearchLastHistories(self):
        #search the index of last run that saved in output folder
        #search the file extension of the first item in ext_filter.txt
        for fileName in os.listdir(self.outputDir):
            root, extension = os.path.splitext(os.path.join(self.outputDir, fileName))
            if extension == self.targetExt[0]:
                fileName = root.split("/")[-1]
                header = fileName.split("_")[0]
                #check the index of header
                try:
                    index = int(header.replace(self.outputHeader, ""))
                except:
                    errorMsg = "output header " + "'" + header + "'" + " of the file " + "'" + fileName + "'" + " has strange format"
                    errorMsg += ", it should have " + self.outputHeader + "000_" + " format on the first of the file name"
                    raise ValueError(errorMsg)
                self.numPreResult = max(index, self.numPreResult)
        print("Index of the last run:", self.numPreResult)
        print("===========================================================")

    def _CpyResult(self, folderIndex):
        #copy all results that have the file extension that match to the list
        fromDir = os.path.join(self.rootDir, self.folderHeader + str(folderIndex))
        toDir = os.path.join(self.rootDir, self.outputDir)
        self.numPreResult += 1
        for fileName in os.listdir(fromDir):
            root, extension = os.path.splitext(os.path.join(fromDir, fileName))
            if extension in self.targetExt:
                nameWithHeader = self.outputHeader + str(self.numPreResult) + "_" + fileName
                shutil.copy(os.path.join(fromDir, fileName),
                            os.path.join(toDir, nameWithHeader))
        print(self.numPreResult, "th results are saved")


    def _randomInpGen(self, folderIndex):
        # generate the random geometry
        runDir = os.path.join(self.rootDir, self.folderHeader + str(folderIndex))
        self._inp.transRandom()
        self._inp.defectRandom()
        self._inp.write(os.path.join(runDir, self.inpName_FLUKA + ".inp"))
        self._inp.writeInfo(os.path.join(runDir, "geo_info.txt"))

    def _run(self, folderIndex):
        runDir = os.path.join(self.rootDir, self.folderHeader + str(folderIndex))
        os.chdir(runDir)
        self.process[folderIndex] = subprocess.Popen(self.bashCmd.split(), stdout=subprocess.PIPE)
        print("FLUKA is executed on thread", folderIndex)
        print("===========================================================")


if __name__ == "__main__":
    mainloop = MainLoop()
    mainloop.Execute()

"""
Class that reads output data from the acquisition system as well as meta data

CONSTRUCTOR
scan = DataReader(folder,scanNr)
IN
    folder:     path of the folder containing the scan data files
    scanNr:     scan number
OUT
    obj         scan object holding scan definition

FUNCTIONS
getData(self, datatype, samples=[], channels=[], interleaves=[], dynamics=[])
IN
    type:         string data type. Type names are defined by the Acq System output file extensions
    samples:      numpy array of requested samples. If not present or empty ([]) all acquired samples are returned
    channels:     numpy array of requested channels. Relative to acquired channels! If not present or empty ([]) all acquired channels are returned
    interleaves:  numpy array of requested interleaves. If not present or empty ([]) all acquired interleaves are returned
    dynamics:     numpy array of requested dynamics. If not present or empty ([]) all acquired dynamics are returned
OUT
    data:         size = [samples,channels,interleaves,dynamics]

getTriggerTimeData(this)
OUT
    trigTimes     np array with trigger times

EXAMPLE USAGE
import SkopeDataReader
# read scan data
scan = SkopeDataReader.DataReader(dataFolder, scanNr)

# read raw data. sample 0-9999, (rel.)channel 0:4, interleave 0, dynamic 2&4
raw =   scan.getData('raw', samples=np.arange(1000), channels=np.arange(5), interleaves=np.arange(1), dynamics=np.array([2,4]))
# read all phase data
phase = scan.getData('phase')
"""

import os
import json
import struct
import warnings
import numpy as np
import scipy.signal as ss
from SkopeDataReader.AttrDict import AttrDict


class DataReader:

    def __init__(self, folder, scanNr):
        self.fileBaseName = ''
        self.filePath = ''
        self.scanDef = []
        self.aqResults = []

        self.setFilePathAndName(folder, scanNr)
        self.loadScanFile()

    def setFilePathAndName(self, folder, scanNr):
        scanfiles = [f for f in os.listdir(folder) if (f.endswith('.scan') and not f.endswith('_sync.scan'))]
        match = []
        for file in scanfiles:
            id = int(file.split('_', 1)[0])
            if id == scanNr:
                match.append(file)
        if len(match) > 1:
            raise Exception(
                'Multiple files with the same scan number detected! (scan number: %i, folder: %s)' % (scanNr, folder))
        elif len(match) == 0:
            raise Exception('File not found! (scan number: %i, folder: %s)' % (scanNr, folder))
        self.filePath = folder
        self.fileBaseName = os.path.splitext(match[0])[0]

    def loadScanFile(self):
        fh = open(os.path.join(self.filePath, (self.fileBaseName + '.scan')), 'r')
        fileContent = fh.read()
        fh.close()
        try:
            content = AttrDict(json.loads(fileContent))
        except json.JSONDecodeError as err:
            raise json.JSONDecodeError('Scan file is not in JSON format. Can not be read!', err.doc, err.pos)

        if hasattr(content, 'scanDef') & hasattr(content, 'acquisitionResults'):
            self.scanDef = content.scanDef
            self.aqResults = content.acquisitionResults
        else:
            raise ImportError('Scan file could not be parsed correctly')

    # ToDo: add checks for hasattr(obj, attr) befor accessing any info from scanDef / aqRes -> catch changes in either of them

    def getData(self, datatype, samples=[], channels=[], interleaves=[], dynamics=[]):
        fullDataFileName = os.path.join(self.filePath, self.fileBaseName + '.' + datatype)
        if not os.path.exists(fullDataFileName):
            raise Exception('File %s does not exist' % fullDataFileName)

        # set data specific parameters:
        typeIsComplex = False
        if datatype == 'raw':
            typeIsComplex = True
        if datatype == 'kspha':
            typeMaxNrChannels = sum(self.scanDef.data.k.channels)
            typeMaxNrInterleaveSamples = self.scanDef.data.k.nrInterleaveSamples
        elif datatype == 'kcoco':
            typeMaxNrChannels = 4
            typeMaxNrInterleaveSamples = self.scanDef.data.k.nrInterleaveSamples
        else:
            typeMaxNrChannels = sum(getattr(self.scanDef.data, datatype).channels)
            typeMaxNrInterleaveSamples = getattr(self.scanDef.data, datatype).nrInterleaveSamples

        # check for out of bounds:
        if len(channels) > typeMaxNrChannels:
            raise Exception('Number of requested channels (%i) exceeds number of acquired channels (%i) for data type %s' % (len(channels), typeMaxNrChannels, datatype))
        if not set(samples).issubset(np.arange(typeMaxNrInterleaveSamples)):
            raise Exception('Requested samples are not subset of acquired samples for data type %s' % datatype)
        if not set(interleaves).issubset(np.arange(self.scanDef.sequenceParameters.nrInterleaves)):
            raise Exception('Requested interleaves are not subset of acquired interleaves')
        if not set(dynamics).issubset(np.arange(self.aqResults.acquiredDynamics)):
            raise Exception('Requested dynamics are not subset of acquired dynamics')

        # default: read all data if input value was empty
        if len(samples) == 0:
            samples = np.arange(typeMaxNrInterleaveSamples)
        if len(channels) == 0:
            channels = np.arange(typeMaxNrChannels)
        if len(interleaves) == 0:
            interleaves = np.arange(self.scanDef.sequenceParameters.nrInterleaves)
        if len(dynamics) == 0:
            if self.aqResults.acquiredInterleaves > self.aqResults.acquiredDynamics * self.scanDef.sequenceParameters.nrInterleaves:
                dynamics = np.arange(self.aqResults.acquiredDynamics + 1)
                warnings.warn('Not all interleaves of the last dynamic were acquired. Missing interleaves will be zero-padded.', stacklevel=2)
            else:
                dynamics = np.arange(self.aqResults.acquiredDynamics)

        # initialize data array
        data = np.zeros((len(samples), len(channels), len(interleaves), len(dynamics)))
        if typeIsComplex:
            data = data * 1j

        # read data
        fileid = open(fullDataFileName, 'rb')
        for ixDyn in range(len(dynamics)):
            offset_dyn = dynamics[ixDyn] * self.scanDef.sequenceParameters.nrInterleaves * typeMaxNrInterleaveSamples

            for ixInt in range(len(interleaves)):
                offset_int = interleaves[ixInt] * typeMaxNrInterleaveSamples

                offset = (offset_dyn + offset_int) * typeMaxNrChannels * 8    # 8 bytes per channel
                readSize = typeMaxNrInterleaveSamples * typeMaxNrChannels * 8

                fileid.seek(offset, 0)  # set offset at absolute position (0)

                if typeIsComplex:  # complex raw data
                    readdata = np.frombuffer(fileid.read(readSize), dtype='>i4')
                    readdata = readdata[::2] + (readdata[1::2] * 1j)
                else:  # all other data types
                    readdata = np.frombuffer(fileid.read(readSize), dtype='>f8')

                if readdata.size:
                    readdata.shape = (typeMaxNrInterleaveSamples, typeMaxNrChannels)
                    data[:, :, ixInt, ixDyn] = readdata[samples[:,None], channels[None,:]]

        if datatype == 'raw':
            data = data * self.scanDef.processingParameters.rawScalingFactor

        fileid.close()
        return data


    def filterData(self, data, frequencyKHz=50):
        if data.shape[0] == 1:
            raise AttributeError('Filtering not implemented for Bfit / Gfit data')
        if isinstance(data[0,0,0,0], complex):
            raise AttributeError('Filtering not implemented for raw data')
        # Define Filter
        samplingRate = 1 / self.scanDef.data.phase.dt   # Assume sampling rate for phase & k is the same
        sos = ss.butter(20, frequencyKHz*1000, 'lp', fs=samplingRate, output='sos')
        # Apply filter for each channel, dynamic and interleave
        for ixChannel in range(data.shape[1]):
            for ixInterleave in range(data.shape[2]):
                for ixDynamic in range(data.shape[3]):
                    data[:, ixChannel, ixInterleave, ixDynamic] = ss.sosfilt(sos, data[:, ixChannel, ixInterleave, ixDynamic])
        return data


    def getTriggerTimeData(self):
        fileid = open(os.path.join(self.filePath, self.fileBaseName + '.trig'), 'rb')

        VMajor = int(self.scanDef.version.split('.')[0])
        # old file version (up to, and including, Version 2022) -> only trigger times
        if (VMajor < 2023):
            data = np.frombuffer(fileid.read(), dtype='>f8')
        # new file version (starting from Version 2023) -> flags in first byte, trigger time in next 8 bytes
        else:
            binaryData = fileid.read()
            numTrigger = len(binaryData) // 9
            flags = {'monitored': [], 'extTrigger': []}
            data = {'triggerTime': [], 'flags': flags}
            for ix in range(numTrigger):
                # read flags
                flag = binaryData[ix*9]
                data['flags']['monitored'].append(flag&1 != 0)
                data['flags']['extTrigger'].append(flag&2 != 0)
                # read time stamp data
                temp = binaryData[ix*9+1:(ix+1)*9]
                data['triggerTime'].append(struct.unpack('>d', temp)[0])
       
        fileid.close()
        return data

from unittest import TestCase
import os
import json
import numpy as np
from SkopeDataReader.DataReader import DataReader
from SkopeDataReader.AttrDict import AttrDict


def getScanNrFromFileName(fileName):
    scanNr = int(fileName.split('_')[0])
    return scanNr


class TestDataReader(TestCase):
    skopefParentDirectory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    testDataFolder = os.path.join(skopefParentDirectory, r'MatlabAqSysDataImport\testData')

    def setUp(self):
        testDataFolder2020 = os.path.join(self.testDataFolder, '2020.1.0000-TestData')
        self.dataReader = DataReader(testDataFolder2020, 12)

    def test_initialize(self):
        self.assertIsInstance(self.dataReader.scanDef, AttrDict)

    def test_initialize_non_existing_scan(self):
        testDataFolder2020 = os.path.join(self.testDataFolder, '2020.1.0000-TestData')
        self.assertRaises(Exception, DataReader, testDataFolder2020, 11)

    def test_initialize_non_existing_folder(self):
        testDataFolder = os.path.join(self.testDataFolder, 'nonExisting')
        self.assertRaises(FileNotFoundError, DataReader, testDataFolder, 1)

    def test_read_scan_files(self):
        folders = os.listdir(self.testDataFolder)
        for folder in folders:
            fullPath = os.path.join(self.testDataFolder, folder)
            scanFiles = [f for f in os.listdir(fullPath,) if f.endswith('.scan')]
            for scanFile in scanFiles:
                scanNr = getScanNrFromFileName(scanFile)
                try:
                    DataReader(fullPath, scanNr)
                except json.JSONDecodeError:
                    print(f'Skipped reading scan \'{folder}\\{scanFile}\' since the scan file is not in JSON format.')
                except:
                    self.fail()

    def test_get_trigger_time_data(self):
        triggerTime = self.dataReader.getTriggerTimeData()
        self.assertEqual(3, triggerTime.size)

    def test_get_data(self):
        subFolders = ['2018.0.0000-TestData', '2020.1.0000-TestData']
        for folder in subFolders:
            testFolder = os.path.join(self.testDataFolder, folder)
            scanNr = getScanNrFromFileName(os.listdir(testFolder)[0])
            DR = DataReader(testFolder, scanNr)
            data = DR.getData('raw')
            self.assertEqual((32000, 16, 1, 3), data.shape)
            data = DR.getData('kspha')
            self.assertEqual((32000, 16, 1, 3), data.shape)
            data = DR.getData('kcoco')
            self.assertEqual((32000, 4, 1, 3), data.shape)

    def test_get_other_data_types(self):
        folder = os.path.join(self.testDataFolder, '2017.0.0000-TestData')
        DR = DataReader(folder, 1)
        data = DR.getData('raw')
        self.assertEqual((20000, 16, 1, 3), data.shape)
        data = DR.getData('phase')
        self.assertEqual((20000, 16, 1, 3), data.shape)
        data = DR.getData('Bfit')
        self.assertEqual((1, 16, 1, 3), data.shape)

    def test_get_partial_data(self):
        data = self.dataReader.getData('raw', dynamics=[0,2])
        self.assertEqual((32000, 16, 1, 2), data.shape)

    def test_out_of_range_sample(self):
        self.assertRaises(Exception, self.dataReader.getData, 'raw', samples=np.arange(100000))

    def test_out_of_range_channel(self):
        self.assertRaises(Exception, self.dataReader.getData, 'raw', channels=np.arange(19))

    def test_out_of_range_interleave(self):
        self.assertRaises(Exception, self.dataReader.getData, 'raw', interleaves=np.array([3]))

    def test_out_of_range_dynamic(self):
        self.assertRaises(Exception, self.dataReader.getData, 'raw', dynamics=np.array([2,4,6]))


# todo: (?)  check if k and positions are in consistency with basis functions
# todo: test processing

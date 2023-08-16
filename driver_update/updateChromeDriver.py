import os
import platform
import requests
import time
from zipfile import ZipFile

import bs4
from bs4 import BeautifulSoup as bs
import lxml.html as lh

import getpass

import traceback

class updateChromeDriver:

    def __init__(self):

        self.osSystem = platform.system()
        
        _initialUrl = 'https://chromedriver.storage.googleapis.com/{}'

        self.__urlChromeDriver = [
            {'URL': _initialUrl + '/chromedriver_mac64.zip', 'OS': 'Darwin'},
            {'URL': _initialUrl + '/chromedriver_win32.zip', 'OS': 'Windows'}
        ]

        self._driverFile = 'chromedriver.exe' if self.osSystem == 'Windows' else 'chromedriver'
        self.textFileVersion = 'chromeVersion.txt'
        self._version = ''
        self._fullVersion = ''

    def checkVersion(self):
        try:
            if self.osSystem == 'Windows':

                from win32api import GetFileVersionInfo, LOWORD, HIWORD

                _userName = getpass.getuser()

                _fileNames = [
                    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                    f'C:\\Users\\{_userName}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
                    ]
                
                _fileName = [item for item in _fileNames
                    if os.path.exists(item)][0]

                info = GetFileVersionInfo(_fileName, "\\")

                ms = info['FileVersionMS']
                ls = info['FileVersionLS']

                self._version = '{}.{}.{}.{}'.format(HIWORD (ms), LOWORD (ms), HIWORD (ls), LOWORD (ls))
                self._fullVersion = self._version

            elif self.osSystem == 'Darwin':

                print(self.osSystem)

                from subprocess import Popen, PIPE
                _cmd = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
                _result = Popen(_cmd, shell=True, stdout=PIPE).stdout

                _byte = _result.read()

                self._version = self.onlyNumbers(_byte)

            if not os.path.exists(self._driverFile):
                self.downloadChromeDriver()
                return

            if not os.path.exists(self.textFileVersion):
                with open(self.textFileVersion, 'w') as fi:
                    fi.write(self._version)
                    fi.close()

            _lastVersion = ''

            with open(self.textFileVersion, 'r') as fi:
                _lastVersion = fi.read()
                fi.close()

            self._version = self._version[0: self._version.rfind('.')]
            _lastVersion = _lastVersion[0:_lastVersion.rfind('.')]

            print('Checando atualizações de chromeDriver...')

            if _lastVersion != self._version:
                self.downloadChromeDriver()

        except Exception as ex:
            print(ex.args[0])

    def downloadChromeDriver(self):

        try:
            self.getSpecificVersion()

            _url = [item['URL'].format(self._version) for item in self.__urlChromeDriver
                if item['OS'] == self.osSystem][0]

            _zipFile =  'chromedriver_win32.zip' if self.osSystem == 'Windows' \
                else 'chromedriver_mac64.zip'

            _result = requests.get(_url, stream=True)

            if os.path.exists(self._driverFile):
                os.remove(self._driverFile)

            with open(_zipFile, 'wb') as fi:
                fi.write(_result.content)
                fi.close()

            with ZipFile(_zipFile) as zf:
                zf.extractall()

            os.remove(_zipFile)

            print('{} atualizado para versão {}'.format(self._driverFile.upper(), self._version))

        except Exception as ex:
            print('Erro ao tentar baixar webDriver mais atualizado', 
                  '\n'.join((
                        ex.args[0],
                        traceback.format_exc()
                  ))
            )

    def getSpecificVersion(self):

        print('Baixando a versão correta de chromeDriver...')

        try:
            _html = requests.get('https://chromedriver.chromium.org/downloads')
            _page = bs(_html.content, 'html.parser')

            _listOfAs = _page.findAll('a')

            def findHref(_elm):
                try:
                    return _elm['href']
                except:
                    return None

            self._version = self._version[0:self._version.rfind('.')]

            _links = [_link['href'] for _link in _listOfAs 
                if findHref(_link) is not None and self._version in _link['href']]
            
            _linkToDownload = ''
            
            if len(_links) > 0:
                _linkToDownload = [_link['href'] for _link in _listOfAs 
                    if findHref(_link) is not None and self._version in _link['href']][0]
                
            elif len(_links) == 0:
                _linkToDownload = [_link['href'] for _link in _listOfAs 
                    if findHref(_link) is not None and 'index.html?path=' in _link['href']][0]

            self._version = _linkToDownload[_linkToDownload.rfind('=') + 1:]
            self._version = self.onlyNumbers(self._version)

            self.writeChromeDriverVersion()

        except:
            self._version = self._fullVersion
            self.writeChromeDriverVersion()

    def writeChromeDriverVersion(self):
        print('Gravando a versão atual de chromeDriver...')

        for i in range(3):
            try:
                with open(self.textFileVersion, 'w') as fi:
                    fi.write(self._version)
                    fi.close()
                    break

            except:
                time.sleep(1)

    def onlyNumbers(self, _strByte):
        _version = ''

        if isinstance(_strByte, str):
            _version = _strByte

        elif isinstance(_strByte, bytes):
            _version = _strByte.decode('utf-8').replace('\n', '')

        _nums = '0123456789.'

        retorno = [_version[i:i+1] for i, item in enumerate(_version) 
            if _version[i:i+1] in _nums]

        return ''.join(retorno)

    def __del__(self):
        pass


if __name__ == '__main__':
    up = updateChromeDriver()
    up.checkVersion()
    del up

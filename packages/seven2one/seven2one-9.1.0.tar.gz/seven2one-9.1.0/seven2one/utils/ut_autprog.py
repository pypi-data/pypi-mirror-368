import base64
from typing import Optional
from loguru import logger
import os
from pathlib import Path

class AutProgUtils():

    @staticmethod
    def _upsetFiles(filePaths: list) -> Optional[str]:
        """Converts a list of files to Base64 provides the upsetFiles graphQL format"""

        _files = ''

        for path in filePaths:
            if not os.path.exists(path):
                logger.error(f"Path {path} does not exist.")
                return None
            else:
                fileName = os.path.split(path)[-1]
                contentBase64 = AutProgUtils._encodeBase64(path)
                _files += f'{{fullName: "{fileName}", contentBase64: "{contentBase64}"}},\n'

        return _files

    @staticmethod
    def _getFileNames(filePaths: list) -> str:
        """Returns file names from a file path"""
        return '\r\n'.join([os.path.split(path)[-1] for path in filePaths])

    @staticmethod
    def _encodeBase64(file: str):
        with open(file, mode='r', encoding='utf-8') as f:
            BOM = '\ufeff'
            content = f.read()
            if content.startswith(BOM):
                content = content[1:]
            content = base64.b64encode(content.encode('utf-8'))
            return content.decode('utf-8')

    @staticmethod
    def _varsToString(vars: dict, type) -> str:
        """Transforms a dict of function variables to a string. All values will be 
            converted to string.
        """
        if type == 'input':
            type = 'inputVariables'
        elif type == 'env':
            type = 'environmentVariables'
        else:
            return ''

        _vars = f'{type}: [\n'
        for key, value in vars.items():
            _vars += f'{{key: "{key}", value: "{str(value)}"}}\n'

        _vars += '\n]'

        return _vars

    @staticmethod
    def _downloadFunctionFile(path, fileName, content):
        fullPath = path + fileName
        dir = os.path.dirname(fullPath)
        Path(dir).mkdir(parents=True, exist_ok=True)
        with open(fullPath, 'w', encoding="utf-8") as f:
            f.write(base64.b64decode(content).decode('UTF8'))

from enum import Enum
import os, sys, json, math
class ReturnValues(Enum):
    """
    Enum representing possible return values from functions.
    """
    SUCCESS = 0
    ERROR = 1
    CRED_CREATE_SUCCESS = 2
    CRED_CREATE_ERROR = 3
    CRED_FOUND = 4 
    CRED_NOT_FOUND = 5
    ENGINE_FOUND = 6
    ENGINE_NOT_FOUND = 7
    ENGINE_CREATE_SUCCESS = 8
    ENGINE_CREATE_ERROR = 9
    ENGINE_REMOVE_SUCCESS = 10
    ENGINE_REMOVE_ERROR = 11
    ENGINE_DEPLOY_SUCCESS = 12
    ENGINE_DEPLOY_ERROR = 13

    # UPT Repo Engine status
    UPT_ENGINE_CREATE_SUCCESS = 14
    UPT_ENGINE_CREATE_ERROR = 15
    UPT_ENGINE_UPDATE_SUCCESS = 16
    UPT_ENGINE_UPDATE_ERROR = 17
    UPT_ENGINE_DELETE_SUCCESS = 18
    UPT_ENGINE_DELETE_ERROR = 19

    UPT_ENGINE_GET_LAST_DEPLOY_LOGS_SUCCESS = 20
    UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR = 21

    UPT_ENGINE_PULL_SUCCESS = 22
    UPT_ENGINE_PULL_ERROR = 23

    # File Operation Ret
    DIR_FILE_OP_SUCCESS = 100
    DIR_FILE_OP_ERROR = 101
    

class DirFileHandlers:
    def __init__(self):
        pass

    def getFileContent(self, absFilePath: str, readMode: str = "r"):

        if not os.path.exists(absFilePath):
            print (f"Requested file {absFilePath} does not exist!!")
            return None
        
        content : str | None = None
        try:
            with open(absFilePath, readMode) as readFile:
                content = readFile.read()
            return content
        except Exception as e:
            print (f"Exception Occured while fetching file content: {e}")
            return None
        
    def writeFileContent(self, absFilePath: str, writeContent: str, writeMode: str = "w"):
        
        try:
            with open(absFilePath, writeMode) as writeFile:
                writeFile.write(writeContent)
        except Exception as e:
            print (f"Exception Occured while writing the file content: {e}")
            return None
        

    def resolvePath(self, path: str, currDir: str = os.getcwd()):
        
        absPath = os.path.join(currDir, path)
        
        if os.path.exists(absPath):
            return (True, absPath)
        
        
        if os.path.exists(path):
            return (True, path)
        
        
        # print (f"Error in resolving paths for relative path: {path} and absolute path: {absPath}")
        return (False, path)
    
    def fileSizeAndUnits(self, sizeInBytes: int):

        if sizeInBytes == 0:
            return "0 bytes"

        units = ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
        unit_index = int(math.floor(math.log(sizeInBytes, 1024)))
        formatted_size = round(sizeInBytes / (1024 ** unit_index), 2)

        return f"{formatted_size} {units[unit_index]}"

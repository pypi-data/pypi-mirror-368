import os, json, shutil, subprocess, time, sys
import requests
from .unitypredictUtils import ReturnValues as Ret
from .unitypredictUtils import DirFileHandlers
from .UnityPredictLocalHost import UnityPredictLocalHost

import traceback

class UnityPredictCli:
    def __init__(self, uptResponseTimeout: int = 20, uptVerbose: bool = False) -> None:

        self._uptCredFolder = ".unitypredict"
        self._uptCredFile = "credentials"
        self._userRoot = os.path.expanduser("~")
        self._uptCredDir = os.path.join(self._userRoot, self._uptCredFolder)
        self._uptCredPath = os.path.join(self._uptCredDir, self._uptCredFile)

        # self._uptEntryPointAPI = "https://api.dev.unitypredict.net/api/engines/supportedengines"
        self._uptEntryPointAPI = "https://api.prod.unitypredict.com/api/engines/supportedengines"
        self._uptEntryPointFieName = "EntryPoint.py"

        # API list
        self._uptDevAPI = "https://api.dev.unitypredict.net"
        self._uptProdAPI = "https://api.prod.unitypredict.com"
        self._uptEngineAPI = "/api/engines"
        self._uptSupportedPlatforms = "/api/engines/supportedengines"
        self._uptBuildLogsAPI = "/api/engines/buildlogs"

        self._uptBasePlatformName = "SL_CPU_BASE_PYTHON_3.12"
        self._uptLocalMainFileName = "main.py"
        self._uptRequirementFileName = "requirements.txt"

        # Config and its keys
        self._uptEngineConfig = {}
        self._uptAppEngineConfigKey = "LocalMockEngineConfig"
        self._uptDeploymentParametersConfigKey = "DeploymentParameters"
        self._uptEngineIdConfigKey = "UnityPredictEngineId"
        self._uptParentRepoIdConfigKey = "ParentRepositoryId"
        self._uptSelectedBaseImageConfigKey = "SelectedBaseImage"

        self._isContainerDeploy = False
        self._supportedDefaultBaseImages = [] # List of default base images

        self._uptResponseTimeout = uptResponseTimeout

        self._uptUploadTimeout = 600
        self._uptDeployTimeout = 600

        self._uptVerbose = uptVerbose
        self._uptForceDeploy = False

        # Util Driver
        self._dirFileHandlers = DirFileHandlers()
        
        # Get API key
        self._uptApiKeyHeaderPrefix = "APIKEY@"
        self._uptApiKeyDict = {}
        if os.path.exists(self._uptCredPath):
            with open(self._uptCredPath) as credFile:
                self._uptApiKeyDict = json.load(credFile)
            

    # Set CLI parameters
    def setUptUploadTimeout(self, uploadTimeout: int = 600):

        self._uptUploadTimeout = uploadTimeout

    def setUptDeployTimeout(self, deployTimeout: int = 600):

        self._uptDeployTimeout = deployTimeout

    def setUptForceDeploy(self, forceDeploy: bool = False):

        self._uptForceDeploy = forceDeploy
    
    
    # Private API functions
    def _getEnvAPIUrl(self, uptEnv: str = "dev", uptProfile: str = "default"):

        if self._uptVerbose:
            print(f"Getting API URL for environment: {uptEnv} and profile: {uptProfile}")

        endpointPrefix = self._uptApiKeyDict[uptProfile].get("API_URL", "")

        if endpointPrefix != "":
            
            if self._uptVerbose:
                print(f"Using API URL: {endpointPrefix}")
            
            return endpointPrefix
        
        if uptEnv == "prod":
            endpointPrefix = self._uptProdAPI
        else:
            endpointPrefix = self._uptDevAPI

        if self._uptVerbose:
                print(f"Using API URL: {endpointPrefix}")
        
        return endpointPrefix
    
    def _checkEnginePlatform(self, platformName: str, uptProfile: str = "default", uptEnv: str = "dev"):

        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        endpoint = f"{endpointPrefix}{self._uptSupportedPlatforms}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.get(endpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                return Ret.ERROR
            
            respJson = response.json()
            
            suppPlatformNames = {}
            platformDetails = {}
            for supPlatform in respJson:
                platformKey = supPlatform.get("platformKey", "")
                platFriendlyName = supPlatform.get("friendlyName", "")
                suppPlatformNames[platformKey] = platFriendlyName
                platformDetails[platformKey] = supPlatform

            if platformName not in suppPlatformNames.keys():
                print (f"Invalid engine platform {platformName} detected! Please check the platform name in the config file")
                print (f"Supported platforms: {json.dumps(suppPlatformNames, indent=4)}")
                return Ret.ERROR
            
            
            # print (f"Platform details: {json.dumps(platformDetails, indent=4)}")
            self._isContainerDeploy =  platformDetails.get(platformName, {}).get("containerBasedPlatform", False)
            self._supportedDefaultBaseImages = platformDetails.get(platformName, {}).get("recommendedBaseImages", [])
            
            return Ret.SUCCESS
        except Exception as e:
            print (f"Exception occured while checking engine platform: {e}!")
            return Ret.ERROR
        
    
    def _createEngineOnUpt(self, engineName: str, requestPayload: dict, uptProfile: str = "default", uptEnv: str = "dev"):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        endpoint = f"{endpointPrefix}{self._uptEngineAPI}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.post(endpoint, json=requestPayload, headers=endpointHeader, timeout=self._uptResponseTimeout)

            if response.status_code != 200:
                print (f"Unable to create EngineId for engine {engineName}: {response.text} [{response.status_code}]")
                return None


        

            respJson = response.json()
            createdEngineId = respJson["engineId"]

            return createdEngineId

        except Exception as e:
            print (f"Exception occured while creating EngineId: {e}!")
            return None
        
    def _updateEngineOnUpt(self, engineName: str, requestPayload: dict, uptProfile: str = "default", uptEnv: str = "dev"):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        endpoint = f"{endpointPrefix}{self._uptEngineAPI}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.post(endpoint, json=requestPayload, headers=endpointHeader, timeout=self._uptResponseTimeout)

            if response.status_code != 200:
                print (f"Unable to update Engine {engineName}: {response.text} [{response.status_code}]")
                return Ret.ERROR

            # print (f"Update engine {engineName} Success!")
            return Ret.SUCCESS
        except Exception as e:
            print (f"Exception occured while updating Engine {engineName}: {e}!")
            return Ret.ERROR
        
    def _updateAndFetchEngineDetailsOnUpt(self, engineName: str, requestPayload: dict, uptProfile: str = "default", uptEnv: str = "dev"):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        endpoint = f"{endpointPrefix}{self._uptEngineAPI}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.post(endpoint, json=requestPayload, headers=endpointHeader, timeout=self._uptResponseTimeout)

            if response.status_code != 200:
                print (f"Unable to update Engine {engineName}: {response.text} [{response.status_code}]")
                return Ret.ERROR, None
            
            respJson = response.json()
            engineDetails = respJson

            # print (f"Update engine {engineName} Success!")
            return Ret.SUCCESS, engineDetails
        except Exception as e:
            print (f"Exception occured while updating Engine {engineName}: {e}!")
            return Ret.ERROR, None


    def _searchEngineOnUpt(self, engineName: str, engineId: str, uptProfile: str = "default", uptEnv: str = "dev"):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        searchEndpoint = f"{endpointPrefix}{self._uptEngineAPI}/{engineId}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.get(searchEndpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                return (Ret.ERROR, response)
            
            return (Ret.SUCCESS, response)
        except Exception as e:
            print (f"Exception occured while searching Engine {engineName}: {e}!")
            return (Ret.ERROR, None)
    
    def _deployEngineOnUpt(self, engineName: str, engineId: str, uptProfile: str = "default", uptEnv: str = "dev", permitTimeDiff: int = 600):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        deployEndpoint = f"{endpointPrefix}{self._uptEngineAPI}/{engineId}/deploy"
        if self._uptForceDeploy:
            deployEndpoint = f"{deployEndpoint}?force=true"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        if self._uptVerbose:
            print (f"Deploying Engine {engineName} on {deployEndpoint} ...")

        errorMessage = ""

        try:
            response = requests.post(deployEndpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                print (f"Unable to deploy Engine {engineName}: {response.text} [{response.status_code}]")
                return Ret.ERROR
        except Exception as e:
            print (f"Exception occured while starting deployment of {engineName}: {e}!")
            return Ret.ERROR
        
        # Check status of deployment on UnityPredict
        deployStatusEndpoint = f"{endpointPrefix}{self._uptEngineAPI}/{engineId}"
        if self._uptVerbose:
            print (f"Checking status of deployment of {engineName} on {deployStatusEndpoint} ...")

        startTime = time.time()

        print (f"Check Engine deploy status for: {permitTimeDiff} Seconds")

        deployReadyFlag: bool = False
        respDict : dict = {}

        while (True):

            try:
                response = requests.get(deployStatusEndpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
                
                if response.status_code != 200:
                    errorMessage = response.text
                    break
            
                
                respDict = response.json()
                deployStat: str = respDict.get("status", "")
                
                if deployStat.casefold() == "ready":
                    deployReadyFlag = True
                    break

                elif deployStat.casefold() == "preparingimage" or \
                        deployStat.casefold() == "preparingtoupdate" or \
                        deployStat.casefold() == "deployingimage":
                    
                    endTime = time.time()
                    cleanString = " " * 10
                    print(f"\rDeploying Engine {engineName} | Status: {deployStat} | Time elapsed : {endTime - startTime} Seconds | ... {cleanString} \r", end="")
                    # print(f"Deploying Engine {engineName} | Status: {deployStat} | Time elapsed : {endTime - startTime} Seconds | ... ")

                    if ((endTime - startTime) >= permitTimeDiff):
                        print (f"\nExceeded configured time of {permitTimeDiff} Seconds! Terminating deploy process!")
                        print (f"\nUse --deployTimeout flag to increase the deploy timeout (in Seconds)!")
                        break

                    time.sleep(5)

                    continue

                else:
                    print (f"\nInvalid deploy status received: {deployStat}")
                    break

            except Exception as e:
                pass
            
            time.sleep(1)
        
        if deployReadyFlag == True:
            print ("\n")

            deployErrorStatus = respDict.get("lastBuildResults", {}).get("status", "")
            errorMessages = respDict.get("lastBuildResults", {}).get("errorMessages", None)
            debugMessages = respDict.get("lastBuildResults", {}).get("debugLogMessages", None)

            if (deployErrorStatus.casefold() == "failed"):
                print (f"\nEngine {engineName} deployment Error!")
                print (f"Error Messages: {errorMessages}")
                print (f"Debug Info: {debugMessages}")
                return Ret.ERROR

            print (f"Debug Info: {debugMessages}")
            print (f"Error Messages: {errorMessages}")


            return Ret.SUCCESS
        
        
        print (f"\nEngine {engineName} deployment Error! {errorMessage}")
        return Ret.ERROR
        
    
    def _deleteEngineOnUpt(self, engineName: str, engineId: str, uptProfile: str = "default", uptEnv: str = "dev"):
        
        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        searchEndpoint = f"{endpointPrefix}{self._uptEngineAPI}/{engineId}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.delete(searchEndpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                return Ret.ERROR
        
            return Ret.SUCCESS
        except Exception as e:
            print (f"Exception occured while deleting Engine {engineName}: {e}!")
            return Ret.ERROR
    
    def _getFileUploadUrl(self, engineName: str, engineId: str, fileName: str, fileType: str, uptProfile: str = "default", uptEnv: str = "dev"):

        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        fileToUploadUrl = f"{endpointPrefix}{self._uptEngineAPI}/upload/{engineId}/{fileType}?fileName={fileName}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.get(fileToUploadUrl, headers=endpointHeader, timeout=self._uptResponseTimeout)
            
            if response.status_code != 200:
                print (f"unable to fetch upload url for the file: {fileName}: {response.status_code}")
                return None
        
        

            respJson = response.json()
            publicUploadUrl = respJson["publicUploadLink"]

            # print (f"Url fetch for {fileName} of type {fileType} Success!")

            return publicUploadUrl

        except Exception as e:
            print (f"Exception occured while creating EngineId: {e}")
            return None
        

    def _uploadFileToUploadUrl(self, uploadUrl: str, fileName: str, absFilePath: str, fileType: str = "SourceFile", uptProfile: str = "default", uptEnv: str = "dev"):

        print (f"Uploading {fileType} {fileName} ...")

        fileSize = "0 bytes"
        
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            fileSize = self._dirFileHandlers.fileSizeAndUnits(sizeInBytes=0)
            with open(absFilePath, 'rb') as file:
                fileContent = file.read()
                
                fileSize = self._dirFileHandlers.fileSizeAndUnits(sizeInBytes=len(fileContent))
                print (f"Uploading {fileType} {fileName} of size {fileSize} within {self._uptUploadTimeout} Seconds ... ")
                
                response = requests.put(uploadUrl, data=fileContent, timeout=self._uptUploadTimeout)

                if response.status_code != 200:
                    print(f"Error in uploading file {fileName}: {response.text} [{response.status_code}]")
                    return Ret.ERROR
                

            print (f"Successfully Uploaded {fileType} {fileName} of size {fileSize}!")
            return Ret.SUCCESS
        except Exception as e:
            print (f"Exception occured while uploading file {fileName}: {e}!")
            print (f"Use --uploadTimeout flag to increase the upload timeout for large files (in Seconds)!")
            return Ret.ERROR

    
    def _getFileDownloadUrl(self, engineName: str, engineId: str, fileName: str, fileType: str, uptProfile: str = "default", uptEnv: str = "dev"):

        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        fileToUploadUrl = f"{endpointPrefix}{self._uptEngineAPI}/download/{engineId}/{fileType}?fileName={fileName}"
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        try:
            response = requests.get(fileToUploadUrl, headers=endpointHeader, timeout=self._uptResponseTimeout)
            
            if response.status_code != 200:
                print (f"unable to fetch download url for the file: {fileName}: {response.status_code}")
                return None
            else:
                print (f"Download link for file {fileName} fetch success!")
        
        

            respJson = response.json()
            publicDownloadUrl = respJson["publicDownloadLink"]

            # print (f"Url fetch for {fileName} of type {fileType} Success!")

            return publicDownloadUrl

        except Exception as e:
            print (f"Exception occured while creating EngineId: {e}")
            return None
        
    def _downloadFileFromDownloadUrl(self, downloadUrl: str, fileName: str, absFilePath: str, fileType: str = "SourceFile", uptProfile: str = "default", uptEnv: str = "dev"):

        print (f"downloading {fileType} {fileName} ...")

        fileSize = "0 bytes"
        
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        
        try:
            response = requests.get(downloadUrl, timeout=self._uptResponseTimeout)

            if response.status_code != 200:
                print(f"Error in downloading file {fileName}: {response.text} [{response.status_code}]")
                return Ret.ERROR
                

            print (f"Successfully downloaded {fileType} {fileName} with the following contents: \n{response.text}!")
            return Ret.SUCCESS
        except Exception as e:
            print (f"Exception occured while downloading file {fileName} : {e}!")
            return Ret.ERROR


    


    # Private Unitl Functions

    def _getEngineConfigDetails(self, engineName: str):
        
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)
        configName = "config.json"
        engineConfigPath = os.path.join(enginePath, configName)

        configContent = self._dirFileHandlers.getFileContent(engineConfigPath)
        if configContent == None:
            return Ret.ERROR
        
        try:
            self._uptEngineConfig = json.loads(configContent)
            return Ret.SUCCESS
        except Exception as e:
            return Ret.ERROR
        
    def _setEngineConfigDetails(self, engineName: str, configContent: str):
        
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)
        configName = "config.json"
        engineConfigPath = os.path.join(enginePath, configName)

        try:
            self._dirFileHandlers.writeFileContent(engineConfigPath, configContent)
            return Ret.SUCCESS
        except Exception as e:
            return Ret.ERROR
        
    def _uploadReqFile(self, engineName: str, engineId: str, uptProfile: str = "default", uptEnv: str = "dev"):

        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)

        # Upload Requirements File

        reqFilePath = os.path.join(enginePath, self._uptRequirementFileName)
        reqFileName : str = None

        fileUploadUrl: str = None

        if os.path.exists(reqFilePath):
            
            fileUploadUrl = self._getFileUploadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile", uptEnv=uptEnv, uptProfile=uptProfile)
            
            if fileUploadUrl != None:

                ret = self._uploadFileToUploadUrl(uploadUrl=fileUploadUrl, fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile",
                                            absFilePath=reqFilePath)
                
                if ret == Ret.ERROR:
                    reqFileName = None
                else:
                    reqFileName = self._uptRequirementFileName

                    try:
                        downloadUrl = self._getFileDownloadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile", uptEnv=uptEnv, uptProfile=uptProfile)
                        
                        if (downloadUrl != None):
                            # ret = self._downloadFileFromDownloadUrl(downloadUrl=downloadUrl, fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile",
                            #                 absFilePath=reqFilePath)
                            self._reqFileUploadFail = False
                        else:
                            self._reqFileUploadFail = True


                    except Exception as e:
                        print ("Error occured while fetching req info")
        
        return reqFileName
        

    
    def _uploadLocalFiles(self, engineName: str, engineId: str, uptProfile: str = "default", uptEnv: str = "dev"):
        
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)

        # Upload Requirements File

        reqFilePath = os.path.join(enginePath, self._uptRequirementFileName)
        reqFileName : str = None

        fileUploadUrl: str = None

        if os.path.exists(reqFilePath):
            
            fileUploadUrl = self._getFileUploadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile", uptEnv=uptEnv, uptProfile=uptProfile)
            
            if fileUploadUrl != None:

                ret = self._uploadFileToUploadUrl(uploadUrl=fileUploadUrl, fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile",
                                            absFilePath=reqFilePath)
                
                if ret == Ret.ERROR:
                    reqFileName = None
                else:
                    reqFileName = self._uptRequirementFileName

                    try:
                        downloadUrl = self._getFileDownloadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile", uptEnv=uptEnv, uptProfile=uptProfile)
                        
                        if (downloadUrl != None):
                            # ret = self._downloadFileFromDownloadUrl(downloadUrl=downloadUrl, fileName=self._uptRequirementFileName, fileType="PackageDefinitionFile",
                            #                 absFilePath=reqFilePath)
                            self._reqFileUploadFail = False
                        else :
                            self._reqFileUploadFail = True


                    except Exception as e:
                        print ("Error occured while fetching req info")

        # Upload source files
        mainFile: str = "main.py"
        excludedExtensions: list = [".env", ".md", ".gitignore", ".DS_Store", "Thumbs.db"]
        excludedFiles: list = ["config.json"]

        fileUploadList: list = []

        for items in os.listdir(enginePath):
            
            filePath = os.path.join(enginePath, items)

            # Skip main.py, directories, and excluded file types
            if (items == mainFile) or (not os.path.isfile(filePath)):
                continue
            
            # Check if file is in the excluded files list
            if items in excludedFiles:
                continue
            
            # Check if file has an excluded extension
            fileExtension = os.path.splitext(items)[1].lower()
            if fileExtension in excludedExtensions:
                continue

            fileUploadUrl = self._getFileUploadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=items, fileType="SourceFile", uptEnv=uptEnv, uptProfile=uptProfile)
            
            if fileUploadUrl == None:
                continue

            ret = self._uploadFileToUploadUrl(uploadUrl=fileUploadUrl, fileName=items,
                                            absFilePath=filePath)
            
            if ret == Ret.ERROR:
                continue
            
            fileDescription =   {
                                    "fileName": f"{items}",
                                    "fileType": "SourceFile"
                                }
            
            fileUploadList.append(fileDescription)
        
        
        # Upload model files
        modelFolder = self._uptEngineConfig.get("ModelsDirPath", "")
        pathstat, modelFolder = self._dirFileHandlers.resolvePath(path=modelFolder, currDir=enginePath)

        if not pathstat:
            return (fileUploadList, reqFileName)
        
        
        for items in os.listdir(modelFolder):
            
            filePath = os.path.join(modelFolder, items)

            fileUploadUrl = self._getFileUploadUrl(engineName=engineName, engineId=engineId, 
                                   fileName=items, fileType="ModelFiles", uptEnv=uptEnv, uptProfile=uptProfile)
            
            if fileUploadUrl == None:
                continue

            ret = self._uploadFileToUploadUrl(uploadUrl=fileUploadUrl, fileName=items, fileType="ModelFile",
                                            absFilePath=filePath)
            
            if ret == Ret.ERROR:
                continue
            
            fileDescription =   {
                                    "fileName": f"{items}",
                                    "fileType": "ModelFiles"
                                }
            
            fileUploadList.append(fileDescription)

        return (fileUploadList, reqFileName)



    def _fetchEntryPointTemplate(self, apiKey : str, uptProfile: str = "default"):

        # print ("Fetching EntryPoint.py template ...")
        headers = {"Authorization": f"Bearer {apiKey}"}
        
        try:
            
            response = requests.get(self._uptEntryPointAPI, headers=headers, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                print (f"EntryPoint.py template fetch Failure with error code: {response.status_code}")
                print(response.text)
                return Ret.ENGINE_CREATE_ERROR
        
            suppPlatforms = response.json()
            for suppPlatform in suppPlatforms:
                if suppPlatform["platformKey"] != self._uptBasePlatformName:
                    continue

                entrypointResp = requests.get(suppPlatform["entryPointTemplateUrl"], timeout=self._uptResponseTimeout)
                if entrypointResp.status_code != 200:
                    print (f"EntryPoint.py template fetch Failure with error code: {entrypointResp.status_code}")
                    print(entrypointResp.text)
                    return Ret.ENGINE_CREATE_ERROR
                

                entrypointContent = entrypointResp.content.decode(entrypointResp.encoding)
                entrypointContent = entrypointContent.replace("\r", "")
                entryPointFile = os.path.join(os.getcwd(), self._uptEntryPointFieName)

                with open(entryPointFile, "w+", encoding="utf-8") as efile:
                    efile.write(entrypointContent)

                break

        except Exception as e:
            print (f"Exception Occured while fetching EntryPoint: {e}")
            return Ret.ENGINE_CREATE_ERROR
        
        # print ("EntryPoint.py template fetch Success!")
        
        return Ret.ENGINE_CREATE_SUCCESS
    
    def _generateMainFile(self):

        mainFileContent = r"""
from unitypredict_engines import UnityPredictLocalHost
from unitypredict_engines import ChainedInferenceRequest, ChainedInferenceResponse, FileReceivedObj, FileTransmissionObj, IPlatform, InferenceRequest, InferenceResponse, OutcomeValue
import EntryPoint

if __name__ == "__main__":

    
    platform = UnityPredictLocalHost()

    testRequest = InferenceRequest()
    # User defined Input Values
    testRequest.InputValues = {} 
    results: InferenceResponse = EntryPoint.run_engine(testRequest, platform)

    # Print Outputs
    if (results.Outcomes != None):
        for outcomKeys, outcomeValues in results.Outcomes.items():
            print ("\n\nOutcome Key: {}".format(outcomKeys))
            for values in outcomeValues:
                infVal: OutcomeValue = values
                print ("Outcome Value: \n{}\n\n".format(infVal.Value))
                print ("Outcome Probability: \n{}\n\n".format(infVal.Probability))
    
    # Print Error Messages (if any)
    print ("Error Messages: {}".format(results.ErrorMessages))

        """

        try:
            MAIN_FILE_PATH = os.path.join(os.getcwd(), self._uptLocalMainFileName)
            with open(MAIN_FILE_PATH, "w+") as mainf:
                mainf.write(mainFileContent)
        except Exception as e:
            print (f"Exception occured while generating main file: {e}")
            return Ret.ENGINE_CREATE_ERROR
        
        # print ("Main file generation Success!")
        return Ret.ENGINE_CREATE_SUCCESS
    
    def _createRequirementsFile(self):
        
        try:
            REQ_FILE_PATH = os.path.join(os.getcwd(), self._uptRequirementFileName)
            with open(REQ_FILE_PATH, "w+") as mainf:
                pass
        except Exception as e:
            print (f"Exception occured while generating requirements file: {e}")
            return Ret.ENGINE_CREATE_ERROR
        
        # print ("Requirements file generation Success!")
        return Ret.ENGINE_CREATE_SUCCESS
    
    def _createDockerCommandsFile(self):
        """Creates a DockerCommands.txt file with instructions for building and running Docker containers"""
        try:
            DOCKER_FILE_PATH = os.path.join(os.getcwd(), "AdditionalDockerCommands.txt")
            with open(DOCKER_FILE_PATH, "w+") as mainf:
                pass
        except Exception as e:
            print (f"Exception occured while generating docker commands file: {e}")
            return Ret.ENGINE_CREATE_ERROR
        
        print ("Additional Docker command file generation Success!")
        return Ret.ENGINE_CREATE_SUCCESS
    
    def _setDockerCommandsFile(self, dockerCommands: str):
        """Sets a DockerCommands.txt file with instructions for building and running Docker containers"""
        try:
            DOCKER_FILE_PATH = os.path.join(os.getcwd(), "AdditionalDockerCommands.txt")
            with open(DOCKER_FILE_PATH, "w+") as mainf:
                mainf.write(dockerCommands)
        except Exception as e:
            print (f"Exception occured while generating docker commands file: {e}")
            return Ret.UPT_ENGINE_UPDATE_ERROR
        
        print ("Additional Docker command file generation Success!")
        return Ret.UPT_ENGINE_UPDATE_SUCCESS

    def _getAdditionalDockerCommands(self, engineName: str) -> str:
        # 1. Check config.json first
        additionalCommands = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("AdditionalDockerCommands", "")
        if additionalCommands != "":
            return additionalCommands

        # 2. Check for AdditionalDockerCommands.txt file
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)
        dockerCommandsFile = os.path.join(enginePath, "AdditionalDockerCommands.txt")

        # print (f"Docker Commands File: {dockerCommandsFile}")
        
        if os.path.exists(dockerCommandsFile):
            try:
                with open(dockerCommandsFile, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"Error reading AdditionalDockerCommands.txt: {e}")
                
        # 3. Return empty string if neither source has commands
        return ""

    def _createEngineId(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):
    
        parentRepositoryId = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptParentRepoIdConfigKey, "")
        if parentRepositoryId == "":
            print ("No Parent Repository ID provided! Cannot create EngineId without the Parent Repository!")
            print ("Please configure the ParentRepositoryId in the config.json")
            return (None, Ret.UPT_ENGINE_CREATE_ERROR)

        # Create payload to fetch the created engineId
        requestPayload = {
            "engineName":f"{engineName}",
            "parentRepositoryId":f"{parentRepositoryId}",
            "engineDescription":"",
            "packageDefinitionFileName": self._uptRequirementFileName,
            "additionalDockerCommands": self._getAdditionalDockerCommands(engineName),
            "engineId":None
        }

        # Add selectedBaseImage if it exists in config
        selectedBaseImage = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptSelectedBaseImageConfigKey, "")
        if selectedBaseImage:
            requestPayload["selectedBaseImage"] = selectedBaseImage

        createdEngineId = self._createEngineOnUpt(engineName=engineName, requestPayload=requestPayload, uptEnv=uptEnv, uptProfile=uptProfile)
        
        if createdEngineId == None:
            return (None, Ret.UPT_ENGINE_CREATE_ERROR)
        
        return (createdEngineId, Ret.UPT_ENGINE_CREATE_SUCCESS)

    def _fetchOrCreateEngineId(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):
        
        try:
            engineId = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptEngineIdConfigKey, "")
            if engineId != "":

                searchStat, response = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

                if searchStat == Ret.ERROR:
                    print (f"Invalid engine id detected! Creating new Engine {engineName} and assigning new EngineId")
                    return self._createEngineId(engineName=engineName, uptEnv=uptEnv, uptProfile=uptProfile)
                    
                engineDetails: dict = response.json()
                return (engineDetails.get("engineId", None), Ret.UPT_ENGINE_UPDATE_SUCCESS)

            else:
                # Create engine id
                print (f"No engine id detected! Creating new Engine {engineName} and assigning new EngineId")
                return self._createEngineId(engineName=engineName, uptEnv=uptEnv, uptProfile=uptProfile)
        except Exception as e:
            print (f"Exception ocured while fetching EngineId: {e}")
            return (None, Ret.UPT_ENGINE_UPDATE_ERROR)
        
    def _updateBaseConfig(self, engineName: str, key: str, value: str):

        try:
            self._uptEngineConfig[self._uptDeploymentParametersConfigKey][key] = value

            configContent = json.dumps(self._uptEngineConfig, indent=4)

            ret = self._setEngineConfigDetails(engineName=engineName, configContent=configContent)
            if ret == Ret.SUCCESS:
                return Ret.UPT_ENGINE_UPDATE_SUCCESS
            print ("Error occured while updating config file")
            return Ret.UPT_ENGINE_UPDATE_ERROR
        except Exception as e:
            print (f"Exception ocured while updating local config with EngineId: {e}")
            return Ret.UPT_ENGINE_UPDATE_ERROR
        

    def _updateAdditionalDockerCommandsFile(self, engineName: str, additionalDockerCommands: str):

        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)
        engineDockerCommandsFile = os.path.join(enginePath, "AdditionalDockerCommands.txt")

        additionalDockerCommands = additionalDockerCommands.strip()
        additionalDockerCommands = additionalDockerCommands.replace("\r", "")
        
        try:
            with open(engineDockerCommandsFile, "w+") as f:
                f.write(additionalDockerCommands)
        except Exception as e:
            print (f"Exception occured while updating additional docker commands file: {e}")
            return Ret.UPT_ENGINE_UPDATE_ERROR
        
        return Ret.UPT_ENGINE_UPDATE_SUCCESS



    # Binding functions with CLI Flags
    def configureCredentials(self, uptApiKey: str| None, uptProfile: str = "default"):

        if not os.path.exists(self._uptCredDir):

            os.mkdir(self._uptCredDir)
            
        self._uptApiKeyDict[uptProfile] = {
                "UPT_API_KEY": uptApiKey
            }
        
        try:
            with open(self._uptCredPath, "w+") as credFile:
                credFile.write(json.dumps(self._uptApiKeyDict, indent=4))
        except Exception as e:
            print (f"Error in creating file {self._uptCredPath}: {e}")
            return Ret.CRED_CREATE_ERROR
        
        return Ret.CRED_CREATE_SUCCESS
    
    def showProfiles(self):
        
        print ("Credential Profiles: ")
        for keys in self._uptApiKeyDict.keys():
            print(f"{keys}")

        print(f"\n\nTo add API Key for another profile, use the unitypredict --configure --profile <profileName>")

    def findEngine(self, engineName: str, uptProfile: str = "default"):
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)

        if os.path.exists(enginePath):
            return Ret.ENGINE_FOUND
        else:
            return Ret.ENGINE_NOT_FOUND

    
    def createEngine(self, engineName: str, uptProfile: str = "default"):
        
        ret = self.findEngine(engineName=engineName)

        if ret == Ret.ENGINE_FOUND:
            print ("""The engine already exists on the current directory. You can:
                - Change the directory
                - Use [--create] flag to change the name of the engine
                """)
            return ret

        
        currPath = os.getcwd()
        enginePath = os.path.join(currPath, engineName)
        
        # Make Engine Path
        os.mkdir(enginePath)
        
        # Change dir to enginePath
        os.chdir(enginePath)

        
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        # print ("Creating Engine Components ...")
        initEngine = UnityPredictLocalHost(apiKey=apiKey, defaultPlatform=self._uptBasePlatformName)
        
        if not initEngine.isConfigInitialized():
            # print ("Engine Components creation Failed!")
            # Change dir back to parent of enginePath    
            os.chdir(currPath)
            return Ret.ENGINE_CREATE_ERROR

        # print ("Engine Components creation Success!")
        
        # Fetch the entrypoint details
        ret = self._fetchEntryPointTemplate(apiKey=apiKey)
        if ret == Ret.ENGINE_CREATE_ERROR:
            # Change dir back to parent of enginePath    
            os.chdir(currPath)
            return ret
        
        # Generate main file
        ret = self._generateMainFile()
        if ret == Ret.ENGINE_CREATE_ERROR:
            # Change dir back to parent of enginePath    
            os.chdir(currPath)
            return ret
        
        # Generate requirements file
        ret = self._createRequirementsFile()
        if ret == Ret.ENGINE_CREATE_ERROR:
            # Change dir back to parent of enginePath    
            os.chdir(currPath)
            return ret

        # Generate Additional DockerCommands file
        ret = self._createDockerCommandsFile()
        if ret == Ret.ENGINE_CREATE_ERROR:
            # Change dir back to parent of enginePath    
            os.chdir(currPath)
            return ret
        
        
        
        # Change dir back to parent of enginePath    
        os.chdir(currPath)    
        return Ret.ENGINE_CREATE_SUCCESS

    def removeEngine(self, engineName: str, uptProfile: str = "default"):

        ret = self.findEngine(engineName=engineName)

        if ret == Ret.ENGINE_FOUND:
            enginePath = os.path.join(os.getcwd(), engineName)
            shutil.rmtree(enginePath)
            return Ret.ENGINE_REMOVE_SUCCESS
        else:
            return Ret.ENGINE_REMOVE_ERROR
    
    def runEngine(self, engineName: str, uptProfile: str = "default"):

        ret = self.findEngine(engineName=engineName)

        if ret == Ret.ENGINE_FOUND:
            currentPath = os.getcwd()
            enginePath = os.path.join(currentPath, engineName)
            # Change dir to enginePath
            os.chdir(enginePath)
            mainFile = os.path.join(enginePath, self._uptLocalMainFileName)
            subprocess.run(["python", mainFile])
            os.chdir(currentPath)
        else:
            print (f"Engine {engineName} not found. Could not run engine!")

    def deployEngine(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):

        ret = self.findEngine(engineName=engineName)
        if ret != Ret.ENGINE_FOUND:
            print (f"Requested Engine {engineName} not found!")
            return Ret.ENGINE_DEPLOY_ERROR
        
        # Fetch config details
        ret = self._getEngineConfigDetails(engineName=engineName)

        if ret == Ret.ERROR:
            return Ret.ENGINE_DEPLOY_ERROR
        
        engineId, retStatus = self._fetchOrCreateEngineId(engineName=engineName, uptProfile=uptProfile, uptEnv=uptEnv)

        if (((retStatus != Ret.UPT_ENGINE_CREATE_SUCCESS) and (retStatus != Ret.UPT_ENGINE_UPDATE_SUCCESS)) or (engineId == None)):
            print (f"Error in fetching EngineId on the UPT Repository. EngineId: {engineId}")
            return Ret.ENGINE_DEPLOY_ERROR
        
        print (f"Fetched EngineId from UPT: {engineId}")

        if (retStatus == Ret.UPT_ENGINE_CREATE_SUCCESS):
            # New engine created, update the local config with the fetched engineId
            print("Updating local config with the newly created EngineId")
            ret = self._updateBaseConfig(engineName=engineName, key=self._uptEngineIdConfigKey, value=engineId)
            if ret == Ret.UPT_ENGINE_UPDATE_ERROR:
                print ("Error occured in updating the engineID to local config")
                return Ret.ENGINE_DEPLOY_ERROR
            
        ret, response = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

        if ret == Ret.ERROR:
            print (f"Error occured in detecting engine: {engineName} on UnityPredict Repository")
            return Ret.ENGINE_DEPLOY_ERROR
        
        
        respDict: dict = {}
        try:
            respDict = response.json()
            if self._uptVerbose:
                print (f"Response after finding engine: {json.dumps(respDict, indent=4)}")
        except Exception as e:
            print (f"Response after finding engine: {response.text}")

        fileList, reqFileName = self._uploadLocalFiles(engineName=engineName, engineId=engineId, uptProfile=uptProfile, uptEnv=uptEnv)

        enginePlatformKey = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("EnginePlatform", "")
        # Check if the engine platform is supported by the UPT 
        ret = self._checkEnginePlatform(platformName=enginePlatformKey, uptProfile=uptProfile, uptEnv=uptEnv)
        if ret == Ret.ERROR:
            return Ret.ENGINE_DEPLOY_ERROR
        
        prevEnginePlatformKey = respDict.get("enginePlatformKey", "")

        if prevEnginePlatformKey != enginePlatformKey:
            respDict["enginePlatformKey"] = enginePlatformKey
            # Post the update to UPT
            ret, engineDetails = self._updateAndFetchEngineDetailsOnUpt(engineName=engineName, requestPayload=respDict, uptProfile=uptProfile, uptEnv=uptEnv)

            if ret == Ret.ERROR:
                print (f"Error occured in updating engine: {engineName} on UnityPredict Repository")
                return Ret.ENGINE_DEPLOY_ERROR
            
            # Fetch the updated engine details from UPT
            ret, updatedResponse = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

            if ret == Ret.ERROR:
                print (f"Error occured in detecting engine after update: {engineName} on UnityPredict Repository")
                return Ret.ENGINE_DEPLOY_ERROR

            respDict = updatedResponse.json()

        respDict["files"] = fileList
        respDict["packageDefinitionFileName"] = reqFileName
        respDict["engineName"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("EngineName", respDict.get("engineName", engineName))
        respDict["engineDescription"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("EngineDescription", "")
        respDict["memoryRequirement"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("Memory", "")
        respDict["storageRequirement"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("Storage", "")
        respDict["maximumRunTime"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("MaxRunTime", "00:30:00")
        respDict["runOnDedicatedInstance"] = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get("RunOnDedicatedInstance", False)
        
        # Add selectedBaseImage if it exists in config
        # Fill this after calling the API endpoint first without these info
        selectedBaseImage = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptSelectedBaseImageConfigKey, "")
        additionalDockerCommands = self._getAdditionalDockerCommands(engineName)


        # print (f"Additional Docker Commands: {additionalDockerCommands}")

        if not self._isContainerDeploy:
            respDict["selectedBaseImage"] = None
            respDict["additionalDockerCommands"] = additionalDockerCommands
        
        if self._isContainerDeploy:
            if selectedBaseImage != "":
                respDict["selectedBaseImage"] = selectedBaseImage
                respDict["additionalDockerCommands"] = additionalDockerCommands
            else:
                # Update the engine on UPT with no base image and no additional docker commands
                ret, engineDetails = self._updateAndFetchEngineDetailsOnUpt(engineName=engineName, requestPayload=respDict, uptProfile=uptProfile, uptEnv=uptEnv)

                # Fetch the updated engine details from UPT
                if ret == Ret.SUCCESS:
                    respDict = engineDetails
                    # print (f"Updated engine details from UPT: {json.dumps(engineDetails, indent=4)}")
                    # print (f"Updated engine details: {json.dumps(respDict, indent=4)}")
                    # Update specific keys in local files
                    # 1. selectedBaseImage
                    print (f"Updating default selectedBaseImage: {respDict['selectedBaseImage']}")
                    if respDict["selectedBaseImage"] == None:
                        selectedBaseImage = ""
                    else:
                        selectedBaseImage = respDict["selectedBaseImage"]
                    self._updateBaseConfig(engineName=engineName, key=self._uptSelectedBaseImageConfigKey, value=selectedBaseImage)
                    # 2. additionalDockerCommands (Update to additionalDockerCommands file)
                    # self._updateBaseConfig(engineName=engineName, key="AdditionalDockerCommands", value=respDict["additionalDockerCommands"])
                    print (f"Updating default additionalDockerCommands: {respDict['additionalDockerCommands']}")
                    if respDict["additionalDockerCommands"] == None:
                        additionalDockerCommands = ""
                    else:
                        additionalDockerCommands = respDict["additionalDockerCommands"]
                    self._updateAdditionalDockerCommandsFile(engineName=engineName, additionalDockerCommands=additionalDockerCommands)

            
        if self._uptVerbose:
            print (f"Response after uploading files to engine: {json.dumps(respDict, indent=4)}")

        ret = self._updateEngineOnUpt(engineName=engineName, requestPayload=respDict, uptProfile=uptProfile, uptEnv=uptEnv)

        if ret == Ret.ERROR:
            print (f"Error in updating engine {engineName} on UnityPredict")
            return Ret.ENGINE_DEPLOY_ERROR

        if (self._reqFileUploadFail):
            reqFileName = self._uploadReqFile(engineName=engineName, engineId=engineId, uptProfile=uptProfile, uptEnv=uptEnv)
            respDict["packageDefinitionFileName"] = reqFileName

            ret = self._updateEngineOnUpt(engineName=engineName, requestPayload=respDict, uptProfile=uptProfile, uptEnv=uptEnv)

            if ret == Ret.ERROR:
                print (f"Error in updating engine {engineName} on UnityPredict")
                return Ret.ENGINE_DEPLOY_ERROR

        

        print (f"Proceeding to deploy Engine {engineName}...")
        ret = self._deployEngineOnUpt(engineName=engineName, engineId=engineId, uptProfile=uptProfile, uptEnv=uptEnv, permitTimeDiff=self._uptDeployTimeout)

        if ret == Ret.ERROR:
            # print (f"Error in deploying engine {engineName} on UnityPredict")
            return Ret.ENGINE_DEPLOY_ERROR
        
        # print (f"Update of Engine {engineName} Success!")
        
        return Ret.ENGINE_DEPLOY_SUCCESS
    
    def getLastDeployLogs(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):

        ret = self.findEngine(engineName=engineName)
        if ret != Ret.ENGINE_FOUND:
            print (f"Requested Engine {engineName} not found!")
            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
        
        # Fetch config details
        ret = self._getEngineConfigDetails(engineName=engineName)

        if ret == Ret.ERROR:
            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
        
        currentPath = os.getcwd()
        enginePath = os.path.join(currentPath, engineName)
        # Change dir to enginePath
        os.chdir(enginePath)

        # Fetch the engineId
        engineId = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptEngineIdConfigKey, "")
        if engineId == "":
            print (f"Error in fetching EngineId on the UPT Repository. EngineId: {engineId}")
            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
        
        searchStat, _ = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

        if searchStat == Ret.ERROR:
            print (f"Error occured in detecting engine {engineName} on UnityPredict Repository")
            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR

        try:
        
            endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
            deployEndpoint = f"{endpointPrefix}{self._uptEngineAPI}/{engineId}/deploy"
            apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
            endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

            deployStatusEndpoint = f"{endpointPrefix}{self._uptBuildLogsAPI}/{engineId}"
            deployStatusResponse = requests.get(deployStatusEndpoint, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if deployStatusResponse.status_code != 200:
                print (f"Error in fetching deploy status for engine {engineName} on UnityPredict: {deployStatusResponse.text}")
                return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
            
            deployStatus = deployStatusResponse.json()
            debugMessagesUrl = deployStatus.get("publicLogsUrl", None)
            if debugMessagesUrl == None:
                print (f"No debug logs available for engine {engineName} on UnityPredict")
                return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
            
            # Download the debug logs
            debugMessagesResponse = requests.get(debugMessagesUrl, timeout=self._uptResponseTimeout)
            if debugMessagesResponse.status_code != 200:
                print (f"Error in fetching debug logs for engine {engineName} on UnityPredict: {debugMessagesResponse.text}")
                return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR
            
            debugMessages = debugMessagesResponse.text
            if self._uptVerbose:
                print (f"Debug logs for engine {engineName} on UnityPredict: ")
                print (debugMessages)
            
            # Clean up any non-UTF8 characters and handle encoding
            debugMessages = debugMessages.encode('utf-8', errors='ignore').decode('utf-8')
            # Save the debug logs to a file
            debugLogsFileName = os.path.join(enginePath, f"DebugLogs.txt")
            debugMessages = debugMessages.encode('utf-8').decode('utf-8')
            with open(debugLogsFileName, "w",  encoding='utf-8') as f:
                f.write(debugMessages)
            
            print (f"Debug logs saved to {debugLogsFileName}")

            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_SUCCESS
        except Exception as e:
            print (f"Error in fetching deploy status and logs for engine {engineName} on UnityPredict: {e} :: Traceback: {traceback.format_exc()}")
            return Ret.UPT_ENGINE_GET_LAST_DEPLOY_LOGS_ERROR


    def deleteDeployedEngine(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):
        
        ret = self.findEngine(engineName=engineName)
        if ret != Ret.ENGINE_FOUND:
            print (f"Requested Engine {engineName} not found!")
            return Ret.UPT_ENGINE_DELETE_ERROR
        
        # Fetch config details
        ret = self._getEngineConfigDetails(engineName=engineName)

        if ret == Ret.ERROR:
            return Ret.UPT_ENGINE_DELETE_ERROR
        
        engineId = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptEngineIdConfigKey, "")
        
        if engineId == "":
            return Ret.UPT_ENGINE_DELETE_ERROR
        
        searchStat, response = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

        if searchStat == Ret.ERROR:
            print (f"Error occured in detecting engine {engineName} on UnityPredict Repository")
            return Ret.UPT_ENGINE_DELETE_ERROR
        
        ret = self._deleteEngineOnUpt(engineName=engineName, engineId=engineId, uptProfile=uptProfile, uptEnv=uptEnv)

        if ret == Ret.ERROR:
            print (f"Error occured in deleting engine {engineName} on UnityPredict Repository")
            return Ret.UPT_ENGINE_DELETE_ERROR
        
        searchStat, response = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)
        
        if searchStat == Ret.ERROR:
            # print (f"Delete engine {engineName} [{engineId}] on UnityPredict Repository Success!")
            return Ret.UPT_ENGINE_DELETE_SUCCESS
        
        return Ret.UPT_ENGINE_DELETE_ERROR
    
    
    
    def _downloadFileFromUpt(self, fileToDownloadUrl: str, endpointHeader: dict):
        try:
            response = requests.get(fileToDownloadUrl, headers=endpointHeader, timeout=self._uptResponseTimeout)
            if response.status_code != 200:
                print (f"Error in downloading file from UPT: {response.text}")
                return None
            
            responseJson = response.json()
            if self._uptVerbose:
                print (f"Response after downloading file from UPT: {json.dumps(responseJson, indent=4)}")
            
            contentResponse = requests.get(responseJson.get("publicDownloadLink", ""), timeout=self._uptResponseTimeout)
            if contentResponse.status_code != 200:
                print (f"Error in downloading file from UPT: {contentResponse.text}")
                return None
            
            return contentResponse.content


        except Exception as e:
            print (f"Error in downloading file from UPT: {e} :: Traceback: {traceback.format_exc()}")
            return None
    
    def _downloadEngineFiles(self, engineName: str, engineId: str, engineDetails: dict, uptProfile: str = "default", uptEnv: str = "dev"):

        endpointPrefix = self._getEnvAPIUrl(uptEnv=uptEnv, uptProfile=uptProfile)
        apiKey = self._uptApiKeyDict[uptProfile]["UPT_API_KEY"]
        endpointHeader = {"Authorization": f"Bearer {self._uptApiKeyHeaderPrefix}{apiKey}"}

        engineFiles = engineDetails.get("files", [])
        reqFileName = engineDetails.get("packageDefinitionFileName", "")
        additionalDockerCommandsContent = engineDetails.get("additionalDockerCommands", "")

        currentPath = os.getcwd()
        enginePath = os.path.join(currentPath, engineName)

        try:
            for engineFile in engineFiles:
                fileType = engineFile.get("fileType", "")
                fileName = engineFile.get("fileName", "")

                if fileType == "":
                    continue
                
                # Download the engine files
                fileToDownloadUrl = f"{endpointPrefix}{self._uptEngineAPI}/download/{engineId}/{fileType}?fileName={fileName}"
                fileContent = self._downloadFileFromUpt(fileToDownloadUrl=fileToDownloadUrl, endpointHeader=endpointHeader)
                if fileContent == None:
                    print (f"Error in downloading source engine file {fileName} for engine {engineName} on UnityPredict")
                    continue

                fileContentStr = fileContent.decode('utf-8') if isinstance(fileContent, bytes) else str(fileContent)
                fileContentStr = fileContentStr.replace("\r\n", "\n")

                
                if fileType == "SourceFile":
                    if self._uptVerbose:
                        print(f"Source engine file content as string for {fileName}: \n{fileContentStr}")
                    localFilePath = os.path.join(enginePath, fileName)
                    with open(localFilePath, "w+", encoding='utf-8') as f:
                        f.write(fileContentStr)
                    print (f"Downloaded source engine file {fileName} to {localFilePath}")
                        

                # Download the model files
                if fileType == "ModelFiles":
                    if self._uptVerbose:
                        print(f"Model engine file content as string for {fileName}: \n{fileContentStr}")
                    # Download model files
                    modelFolder = self._uptEngineConfig.get("ModelsDirPath", "")
                    pathstat, modelFolder = self._dirFileHandlers.resolvePath(path=modelFolder, currDir=enginePath)
                    if pathstat == False:
                        print (f"Error in resolving model folder path: {modelFolder}")
                        continue
                    
                    modelFilePath = os.path.join(modelFolder, fileName)
                    with open(modelFilePath, "w+", encoding='utf-8') as f:
                        f.write(fileContentStr)
                    print (f"Downloaded model file {fileName} to {modelFilePath}")
                    

            # Download the requirements.txt file
            requirementsFilePath = os.path.join(enginePath, reqFileName)
            fileToDownloadUrl = f"{endpointPrefix}{self._uptEngineAPI}/download/{engineId}/PackageDefinitionFile?fileName={reqFileName}"
            fileContent = self._downloadFileFromUpt(fileToDownloadUrl=fileToDownloadUrl, endpointHeader=endpointHeader)
            if fileContent != None:
                fileContentStr = fileContent.decode('utf-8') if isinstance(fileContent, bytes) else str(fileContent)
                fileContentStr = fileContentStr.replace("\r\n", "\n")
                if self._uptVerbose:
                    print(f"{reqFileName} file content as string: \n{fileContentStr}")
                with open(requirementsFilePath, "w+", encoding='utf-8') as f:
                    f.write(fileContentStr)
                print (f"Downloaded {reqFileName} file to {requirementsFilePath}")

            # Download the additionalDockerCommands.txt file
            additionalDockerCommandsFilePath = os.path.join(enginePath, "AdditionalDockerCommands.txt")
            if additionalDockerCommandsContent == None:
                additionalDockerCommandsContent = ""
            additionalDockerCommandsContent = additionalDockerCommandsContent.replace("\r\n", "\n")
            if self._uptVerbose:
                print(f"AdditionalDockerCommands.txt file content as string: \n{additionalDockerCommandsContent}")
            with open(additionalDockerCommandsFilePath, "w+", encoding='utf-8') as f:
                f.write(additionalDockerCommandsContent)
            print (f"Downloaded AdditionalDockerCommands.txt file to {additionalDockerCommandsFilePath}")

            # Config deploy parameters update
            self._updateBaseConfig(engineName=engineName, key="EngineName", value=engineDetails.get("engineName", engineName))
            self._updateBaseConfig(engineName=engineName, key="EngineDescription", value=engineDetails.get("engineDescription", ""))
            self._updateBaseConfig(engineName=engineName, key="EnginePlatform", value=engineDetails.get("enginePlatformKey", ""))
            self._updateBaseConfig(engineName=engineName, key="SelectedBaseImage", value=engineDetails.get("selectedBaseImage", ""))
            self._updateBaseConfig(engineName=engineName, key="Storage", value=engineDetails.get("storageRequirement", 0))
            self._updateBaseConfig(engineName=engineName, key="Memory", value=engineDetails.get("memoryRequirement", 0))
            self._updateBaseConfig(engineName=engineName, key="MaxRunTime", value=engineDetails.get("maximumRunTime", ""))
            self._updateBaseConfig(engineName=engineName, key="ParentRepositoryId", value=engineDetails.get("parentRepositoryId", ""))
            self._updateBaseConfig(engineName=engineName, key="RunOnDedicatedInstance", value=engineDetails.get("runOnDedicatedInstance", False))

            print (f"Updated deploy parameters in config.json for engine {engineName}")

        except Exception as e:
            print (f"Error in downloading engine files: {e} :: Traceback: {traceback.format_exc()}")
            return Ret.UPT_ENGINE_PULL_ERROR
    

    def pullDeployedEngine(self, engineName: str, uptProfile: str = "default", uptEnv: str = "dev"):

        ret = self.findEngine(engineName=engineName)
        if ret != Ret.ENGINE_FOUND:
            print (f"Requested Engine {engineName} not found!")
            return Ret.UPT_ENGINE_PULL_ERROR
        
        # Fetch config details
        ret = self._getEngineConfigDetails(engineName=engineName)

        if ret == Ret.ERROR:
            return Ret.UPT_ENGINE_PULL_ERROR
        
        engineId = self._uptEngineConfig.get(self._uptDeploymentParametersConfigKey, {}).get(self._uptEngineIdConfigKey, "")
        
        if engineId == "":
            print (f"No UnityPredictEngineId detected in config.json for engine {engineName}! Please provide a valid UnityPredictEngineId in config.json")
            return Ret.UPT_ENGINE_PULL_ERROR
        
        searchStat, response = self._searchEngineOnUpt(engineName=engineName, engineId=engineId, uptEnv=uptEnv, uptProfile=uptProfile)

        if searchStat == Ret.ERROR:
            print (f"Error occured in detecting engine {engineName} on UnityPredict Repository")
            return Ret.UPT_ENGINE_PULL_ERROR
        
        respDict = response.json()

        if self._uptVerbose:
            print (f"Response after finding engine: {json.dumps(respDict, indent=4)}")

        self._downloadEngineFiles(engineName=engineName, engineId=engineId, engineDetails=respDict, uptProfile=uptProfile, uptEnv=uptEnv)

        return Ret.UPT_ENGINE_PULL_SUCCESS







        

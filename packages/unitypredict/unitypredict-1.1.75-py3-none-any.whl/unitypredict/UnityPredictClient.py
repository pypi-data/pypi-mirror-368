
from io import IOBase
import json
import os
import time

import requests



class LocalFile:
    fileName: str = ''
    def __init__(self, fileName: str):
        self.fileName = fileName

class UnityPredictFileTransmitDto:

    """
    Represents a file to be transmitted to the UnityPredict API.

    Attributes:
        FileName (str): The name of the file.
        FileHandle (IOBase): The IOBase is a byte stream representation for the file content. This is commonly created by using the python io library's 'open' function.
    """

    FileName: str = ''
    FileHandle: IOBase = None

    def __init__(self, fileName, fileHandle):
        self.FileName = fileName
        self.FileHandle = fileHandle

class UnityPredictFileReceivedDto:
    
    """
    Represents a file received from the UnityPredict API.

    Attributes:
        FileName (str): The name of the file.
        LocalFilePath (str): The local path where the file was saved.
    """
    
    FileName: str = ''
    LocalFilePath: str = ''

    def __init__(self, fileName, localFilePath):
        self.FileName = fileName
        self.LocalFilePath = localFilePath

class UnityPredictRequest:

    """
    Represents a UnityPredict request.

    Attributes:
        ContextId (str): An optional context ID for the request.
        InputValues (dict): A dictionary of input values for the model, where the key is the input variable name and the value of the variable's value.
        DesiredOutcomes (list): A list of desired output variable names.
        OutputFolderPath (str): The target path for saving model's output files (this is optional/not used if the model doesn't produce any output files).
    """

    ContextId: str = ''
    InputValues: dict
    DesiredOutcomes: list
    OutputFolderPath: str

    def __init__(self, ContextId='', InputValues={}, DesiredOutcomes=[], OutputFolderPath=""):
        self.ContextId = ContextId 
        self.InputValues = InputValues 
        self.DesiredOutcomes = DesiredOutcomes 
        self.OutputFolderPath = OutputFolderPath 

    
class UnityPredictResponse:

    """
    Represents a response from the UnityPredict API.

    Attributes:
        ContextId (str): The ID of the request context.
        RequestId (str): The ID of the request.
        ErrorMessages (str): Error messages, if any.
        ComputeCost (float): The estimated compute cost of the request.
        Outcomes (dict): A dictionary containing the processed output values, including file details if applicable.
        Status (str|None): The current status of the request (e.g., "Processing", "Completed", "Error" or None).
    """

    ContextId: str = ''
    RequestId: str = ''
    ErrorMessages: str = ''
    ComputeCost: float = 0.0
    Outcomes: dict = {}
    Status: str|None = None
        
class UnityPredictClient:

    """
    A client class for interacting with the UnityPredict API.

    Attributes:
        ApiKey (str): The API key for authentication.
        ApiBaseUrl (str): The base URL of the UnityPredict API.
        ApiMaxTimeout (int): The maximum wait time (in seconds) for synchronous responses.
    """

    ApiKey: str = ''
    ApiBaseUrl: str = 'https://api.prod.unitypredict.com/api'
    ApiMaxTimeout: int = 12 * 60 * 60


    def __init__(self, apiKey, apiMaxTimeoutInSec = 12 * 60 * 60):
        
        """
        Initializes a UnityPredictClient instance.

        Args:
            apiKey (str): The UnityPredict API key for authentication.
            apiMaxTimeoutInSec (int, optional): The maximum wait time (in seconds) for synchronous responses. Defaults to 12 hours.
        """
        self.ApiKey = f"APIKEY@{apiKey}"
        self.ApiMaxTimeout = apiMaxTimeoutInSec




    def _uploadFileAndStartPredict(self, modelId: str, request: UnityPredictRequest):

        apiKey = self.ApiKey
        apiBaseUrl = self.ApiBaseUrl

        results = UnityPredictResponse()
        needFileUpload = False

        ##### 
        # The request can contain file objects so we need to change those to file names before sending out
        #####
        # first get a list of file that we'll need to upload later & update the POST obj
        for xvarName in request.InputValues:
            if isinstance(request.InputValues.get(xvarName), LocalFile):
                needFileUpload = True
                break

        finalResponseJson: any = ''

        response: requests.Response = None
        if not needFileUpload:
            # serialize the POST obj
            jsonBody = json.dumps(request, default=vars)

            # there are no files to upload so just post normally
            response = requests.post(url = "{}/predict/{}".format(apiBaseUrl, modelId), data=jsonBody, headers={"Authorization": "Bearer {}".format(apiKey)})

            if response.status_code != 200:
                results.ErrorMessages = 'Error from server: {}'.format(response.status_code)
                return (results, {})
            
            finalResponseJson = response.json()
        else:
            # we need to initialize first
            print ("Initializing Platform ...")
            response = requests.post(url = "{}/predict/initialize/{}".format(apiBaseUrl, modelId), data="", headers={"Authorization": "Bearer {}".format(apiKey)})


            if response.status_code != 200:
                results.ErrorMessages = 'Error from server: {}'.format(response.status_code)
                return (results, {})
            
            print ("Platform Initialized!")
            requestId: str = response.json().get('requestId')

            # print (f"Initialized request: {requestId}")
            
            # upload the files
            for xvarName in request.InputValues: 
                if isinstance(request.InputValues.get(xvarName), LocalFile):
                    fileName = request.InputValues.get(xvarName).fileName
                    if not os.path.exists(fileName):
                        results.ErrorMessages = f"File {fileName} does not exist!"
                        return (results, {})
                    fileToUpload: UnityPredictFileTransmitDto = UnityPredictFileTransmitDto(fileName, open(fileName, 'rb'))
                    print (f"Uploading {fileToUpload.FileName}...")
                    response = requests.get(url = "{}/predict/upload/{}/{}".format(apiBaseUrl, requestId, os.path.basename(fileToUpload.FileName)), headers={"Authorization": "Bearer {}".format(apiKey)})
                    if response.status_code != 200:
                        results.ErrorMessages = 'Error from server: {}'.format(response.status_code)
                        return (results, {})
                    uploadLink = response.json().get('uploadLink')
                    fileName = response.json().get('fileName')
                    request.InputValues[xvarName] = fileName # make sure that only the filename is in the request that we are going to POST
                    requests.put(url = uploadLink, data=fileToUpload.FileHandle)
                    print (f"Upload file {fileToUpload.FileName} Success!")
            
            # print (f"Input request: {request.InputValues}")
            jsonBody = json.dumps(request, default=vars)
            
            # print (f"URL: {"{}/predict/{}/{}".format(apiBaseUrl, modelId, requestId)}, body: {jsonBody}")
            response = requests.post(url = "{}/predict/{}/{}".format(apiBaseUrl, modelId, requestId), data=jsonBody, headers={"Authorization": "Bearer {}".format(apiKey)})
            
            if response.status_code != 200:
                results.ErrorMessages = 'Error from server: {}'.format(response.status_code)
                return (results, {})

            finalResponseJson = response.json()

        return (results, finalResponseJson)
    

    def _processPredictedInference(self, responseJson: any, outputFolderPath: str = ""):
        
        results = UnityPredictResponse()

        apiKey = self.ApiKey
        apiBaseUrl = self.ApiBaseUrl
        finalResponseJson = responseJson
        
        finalResponseRequestId: str = finalResponseJson.get('requestId')

        outcomes = finalResponseJson.get('outcomes')
        for outputVarName in outcomes: 
            outcome: list = outcomes.get(outputVarName)
            for outcomeItem in outcome:
                if outcomeItem.get('dataType') == 'File':
                    fileName = outcomeItem.get('value')

                    tempFilePath = os.path.join(tempOutputFolder, fileName)
                    response = requests.get(url = "{}/predict/download/{}/{}".format(apiBaseUrl, finalResponseRequestId, fileName), headers={"Authorization": "Bearer {}".format(apiKey)})
                    with open(tempFilePath, 'wb') as f:
                        f.write(response.content)

                    fileReceived: UnityPredictFileReceivedDto = UnityPredictFileReceivedDto(fileName, tempFilePath)
                    outcomeItem['value'] = fileReceived


        try:
            results.Status = finalResponseJson.get('status')
            results.ComputeCost = finalResponseJson.get('computeCost')
            results.Outcomes = outcomes
            results.RequestId = finalResponseRequestId
            results.ContextId = finalResponseJson.get('contextId')
            results.ErrorMessages = finalResponseJson.get('errorMessages')

        except Exception as e:
            print(e)

        return results
    
    
    def Predict(self, modelId: str, request: UnityPredictRequest) -> UnityPredictResponse:
            
            """
            Sends a synchronous prediction request to the UnityPredict API.

            Args:
                modelId (str): The ID of the model to use for prediction.
                request (UnityPredictRequest): The prediction request object, containing input values, desired outcomes, and output folder path.

            Returns:
                UnityPredictResponse: The response from the UnityPredict API, containing the results and status.
            """
            
            results = UnityPredictResponse()

            apiKey = self.ApiKey
            apiBaseUrl = self.ApiBaseUrl

            needFileUpload: bool = False

            ##### 
            # The request can contain file objects so we need to change those to file names before sending out
            #####
            # first get a list of file that we'll need to upload later & update the POST obj

            
            results, finalResponseJson = self._uploadFileAndStartPredict(modelId=modelId, request=request)

            if (finalResponseJson == {}):
                return results

            statusUrl = ''
            if (finalResponseJson.get('status') == 'Processing'):
                statusUrl = finalResponseJson.get('statusUrl') # this is probably a long-running inference

            loopWaitTime = 0.25
            startTime = time.time()
            maxPredictTime = self.ApiMaxTimeout
            maxTimeExceed = False
            print (f"Starting max inference timer for {maxPredictTime} Seconds")
            while finalResponseJson.get('status') == 'Processing': # todo: add timeout in UnityPredictRequest
                
                if ((time.time() - startTime) > maxPredictTime):
                    print (f"Max time limit of {maxPredictTime} seconds exceeded!")
                    maxTimeExceed = True
                    break
                
                response = requests.get(url = statusUrl, headers={"Authorization": "Bearer {}".format(apiKey)})
                finalResponseJson = response.json()

                delay = min(loopWaitTime, 30)
                time.sleep(delay)

                loopWaitTime *= 2

                print('Waiting {} seconds for job to finish...'.format(delay))

            if maxTimeExceed:
                results = UnityPredictResponse()
                results.Status = None
                results.ErrorMessages = f"Max time limit of {maxPredictTime} seconds exceeded!"
                return results
            
            try:
                results = self._processPredictedInference(responseJson=finalResponseJson, outputFolderPath=request.OutputFolderPath)
                results.Status = finalResponseJson.get('status')
            except Exception as e:
                results = UnityPredictResponse()
                results.Status = None
                results.ErrorMessages = f"Exception Occured while processing Inference: {e}"

            return results
    
    def AsyncPredict(self, modelId: str, request: UnityPredictRequest) -> UnityPredictResponse:

        """
        Initiates an asynchronous inference for the specified model. The function will return the response with a RequestId and Status = 'Processing'. Use the 'GetRequestStatus' function with the returned RequestId to check on the status of the run and retrieve the results.

        Args:
            modelId (str): The Model Id of the specific model you want to invoke.
            request (UnityPredictRequest): The inference request of type UnityPredictRequest, containing input values, desired outputs variables, and an (optional) OutputFolderPath for use with models that generate output files.

        Returns:
            UnityPredictResponse: The initial response from the API, containing the request ID and status.
        """

        try:
        
            results, finalResponseJson = self._uploadFileAndStartPredict(modelId=modelId, request=request)

            results.Status = finalResponseJson.get("status", None)

            if (results.Status == None):

                return results
            
            if (results.Status != "Processing"):

                results = self._processPredictedInference(responseJson=finalResponseJson, outputFolderPath=request.OutputFolderPath)

            else:
                results.Status = finalResponseJson.get('status')
                results.RequestId = finalResponseJson.get('requestId')
                results.ErrorMessages = finalResponseJson.get('errorMessages')

            return results
    
        except Exception as e:
            
            results = UnityPredictResponse()
            results.ErrorMessages = f"Predict Exception Occured: {e}"

            return results
        
    
    def GetRequestStatus(self, requestId: str, outputFolderPath: str = "") -> UnityPredictResponse:


        """
        Retrieves the status of an asynchronous prediction request.

        Args:
            requestId (str): The ID of the asynchronous request.
            outputFolderPath (str, optional): The output folder path for saving results. Defaults to an empty string.

        Returns:
            UnityPredictResponse: The updated response with the current status and results, if available.
        """

        apiKey = self.ApiKey
        apiBaseUrl = self.ApiBaseUrl
        statusUrl: str = "{}/predict/status/{}".format(apiBaseUrl, requestId)

        results: UnityPredictResponse = UnityPredictResponse()

        response = requests.get(url = statusUrl, headers={"Authorization": "Bearer {}".format(apiKey)})
        if response.status_code != 200:
            results.RequestId = requestId
            results.ErrorMessages = 'Error from server: {}'.format(response.status_code)
            return results
        
        finalResponseJson = response.json()

        inferStatus = finalResponseJson.get('status', None)
        results.Status = inferStatus
            
        if (inferStatus == None):
            results.RequestId = requestId
            return results
        
        if (inferStatus == 'Processing'):
            results.RequestId = requestId
            return results

        
        # Once the processing is done
        
        try:
            results = self._processPredictedInference(responseJson=finalResponseJson, outputFolderPath=outputFolderPath)
        except Exception as e:
            results = UnityPredictResponse()
            results.RequestId = requestId
            results.ErrorMessages = f"Exception Occured while processing Inference: {e}"
        
        return results

        

        

        

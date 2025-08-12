from abc import ABCMeta, abstractmethod
from io import BufferedReader, IOBase
import os.path
from enum import Enum

class DataTypes(str, Enum):
    Boolean = 'Boolean'
    Integer = 'Integer'
    Float = 'Float'
    String = 'String'
    File = 'File'
    Tensor = 'Tensor'

class VariableInfo:     
    Data: any
    Type: DataTypes
    def __init__(self, data: any = '', type: DataTypes = DataTypes.String):
        self.Data = data
        self.Type = type

class OutcomeValue:
    """
    Represents a potential outcome with a probability and associated value.

    This class encapsulates both the predicted value and its probability of occurrence,
    allowing for probabilistic inference results.

    Attributes:
        Probability (float): A float value representing the probability of the outcome (0.0 to 1.0).
        Value (any): The value associated with the outcome. Can be any type.
    """

    Probability = 0.0
    Value = None
    DataType: DataTypes

    def __init__(self, value: any = '', probability: float = 0.0, dataType: DataTypes = DataTypes.String):
        self.Probability = probability
        self.Value = value
        self.DataType = dataType
        
class InferenceContextData:
    """
    Stores context metadata related to an inference request.

    When 'Context' is enabled on a model, UnityPredict maintains the engine's context data 
    across multiple invocations within the same user session. This enables persistent storage
    of information like chat history, user preferences, or other historical data that needs 
    to persist between calls.

    Attributes:
        StoredMeta (dict): A dictionary containing key-value pairs representing the stored metadata.
    """

    StoredMeta: dict = {}

    def __init__(self):
        self.StoredMeta = {}

class InferenceRequest:
    """
    Defines the input values, desired outcomes, and context for an inference.

    This class encapsulates all the necessary information to perform an inference operation,
    including the input data, what outcomes are expected, and any contextual information.

    Attributes:
        Inputs (dict): A dictionary containing key-value pairs where the key is the input variable name 
            and the value is a VariableInfo object. This is the recommended way to specify inputs.
        DesiredOutputs (dict): A dictionary containing key-value pairs where the key is the output variable name 
            and the value is a VariableInfo object. This is the recommended way to specify desired outputs.
        InputValues (dict): A legacy dictionary containing key-value pairs representing the input values.
            Consider using Inputs instead for better type safety and metadata.
        DesiredOutcomes (list): A legacy list of strings representing the desired outcomes.
            Consider using DesiredOutputs instead for better type safety and metadata.
        Context (InferenceContextData): An instance of InferenceContextData containing data saved 
            by a prior instance of the engine that was executed for the same ContextId (i.e., same user session).
    """

    Inputs: dict = {}
    DesiredOutputs: dict = {}
    InputValues: dict
    DesiredOutcomes: list
    Context: InferenceContextData = None

    def __init__(self):
        self.Context = InferenceContextData()
        self.Inputs = {}
        self.DesiredOutputs = {}
        self.InputValues = {}
        self.DesiredOutcomes = []
    
class InferenceResponse:
    """
    Represents the response to an inference request, including error messages, costs, and outcome values.

    This class encapsulates all the information returned from an inference operation,
    including any errors encountered, associated costs, and the predicted outcomes.
    It also allows for propagating context to subsequent runs.

    Attributes:
        ErrorMessages (str): A string containing any error messages encountered during the inference.
        CostToModelUser (float): A float value representing the cost of inference that should 
            be charged to the consumer of the model (in US Dollars).
        ReInvokeInSeconds (int): Time to put the engine to sleep before re-invoking it.
        Context (InferenceContextData): An instance of InferenceContextData containing data saved 
            by a prior instance of the engine that was executed for the same ContextId (i.e., same user session).
        Outcomes (dict): A dictionary where the key is the output/outcome variable name and the value is a list of 
            OutcomeValue objects. Each OutcomeValue represents one possible value for the outcome variable. 
            In most cases, there is only one item in the list, and the Value of the first item provides the only value 
            for that outcome.
        Status (str): The current status of the inference request. Can be one of:
            - 'Processing': The inference is still running
            - 'Completed': The inference has finished successfully
            - 'Error': The inference encountered an error
        StatusUrl (str): When Status is 'Processing', this contains the endpoint URL where the status 
            of the request can be checked. This URL can be used to poll for updates on the inference progress.
    """

    ErrorMessages: str = ''
    AdditionalInferenceCosts: float = 0.0
    CostToModelUser: float = 0.0
    ReInvokeInSeconds: int = -1
    Context: InferenceContextData = None
    Outcomes: dict = {}
    StatusUrl: str = ''
    Status: str = ''

    def __init__(self):
        self.ErrorMessages = ''
        self.AdditionalInferenceCosts = 0.0
        self.CostToModelUser = 0.0
        self.ReInvokeInSeconds = -1
        self.Context = InferenceContextData()
        self.Outcomes = {}
        self.StatusUrl = ''
        self.Status = ''

class ChainedInferenceRequest:
    """
    Represents a chained inference request for invoking another model from the current engine.

    This class enables model chaining by allowing the current engine to provide inputs to another
    model using the same input structure. It's primarily used by the invokeUnityPredictModel method.

    Attributes:
        ContextId (str): A string representing the ID of the context for the chained inference.
        InputValues (dict): A dictionary containing key-value pairs representing the input values 
            for the chained inference.
        DesiredOutcomes (list): A list of strings representing the desired outcomes for the chained inference.
    """

    ContextId: str = ''
    InputValues: dict
    DesiredOutcomes: list

    def __init__(self, contextId='', inputValues={}, desiredOutcomes=[]):
        self.ContextId = contextId
        self.InputValues = inputValues
        self.DesiredOutcomes = desiredOutcomes

    
class ChainedInferenceResponse:
    """
    Represents the response to a chained inference request.

    This class encapsulates the results from a chained model invocation, including context ID,
    request ID, error messages, compute cost, and outcome values. It's primarily used by the 
    invokeUnityPredictModel method.

    Attributes:
        ContextId (str): A string representing the ID of the context for the chained inference.
        RequestId (str): A string representing the ID of the individual inference request within the chain.
        ErrorMessages (str): A string containing any error messages encountered during the chained inference.
        ComputeCost (float): A float value representing the compute cost incurred during the chained inference.
        Outcomes (dict): A dictionary containing key-value pairs representing the outcome values 
            for the chained inference.
        Status (str): The current status of the chained inference request. Can be one of:
            - 'Processing': The inference is still running
            - 'Completed': The inference has finished successfully
            - 'Error': The inference encountered an error
        StatusUrl (str): When Status is 'Processing', this contains the endpoint URL where the status 
            of the request can be checked. This URL can be used to poll for updates on the inference progress.
    """

    ContextId: str = ''
    RequestId: str = ''
    ErrorMessages: str = ''
    ComputeCost: float = 0.0
    Outcomes: dict = {}
    StatusUrl: str = ''
    Status: str = ''

    def __init__(self):
        self.ContextId = ''
        self.RequestId = ''
        self.ErrorMessages = ''
        self.ComputeCost = 0.0
        self.Outcomes = {}
        self.StatusUrl = ''
        self.Status = ''


    def getOutputValue(self, outputName: str, index = 0):
        """
        Retrieves an output value from the `Outcomes` dictionary.

        This method provides a convenient way to access specific output values by name and index,
        handling different output formats (dictionary or OutcomeValue objects).

        Args:
            outputName (str): The name of the desired output.
            index (int, optional): The index of the output value to retrieve. Defaults to 0.

        Returns:
            Any: The retrieved output value, or None if not found.
        """
        
        if self.Outcomes == None:
            return None
        
        if outputName not in self.Outcomes:
            return None
        
        if len(self.Outcomes.get(outputName)) > index:
            if isinstance(self.Outcomes.get(outputName)[index], dict):
                return self.Outcomes.get(outputName)[index].get('value')
            elif isinstance(self.Outcomes.get(outputName)[index], OutcomeValue):
                return self.Outcomes.get(outputName)[index].Value
        else:
            return None

class FileTransmissionObj:
    """
    Represents a file to be transmitted on the UnityPredict platform.

    This class encapsulates both the file name and a file handle, providing a unified
    interface for file transmission operations.

    Attributes:
        FileName (str): The name of the file.
        FileHandle (IOBase): A file-like object representing the file's content.
    """

    FileName: str = ''
    FileHandle: IOBase = None

    def __init__(self, fileName, fileHandle):
        self.FileName = fileName
        self.FileHandle = fileHandle

    @classmethod
    def from_path(cls, file_path: str, mode: str = 'rb'):
        """
        Creates a FileTransmissionObj from a file path.

        This factory method provides a convenient way to create a FileTransmissionObj
        directly from a file path, handling the file opening process.

        Args:
            file_path (str): The full path to the file.
            mode (str, optional): The mode to open the file in. Defaults to 'rb'.

        Returns:
            FileTransmissionObj: A new instance with the file name and handle set.

        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            IOError: If there's an error opening the file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_name = os.path.basename(file_path)
        file_handle = open(file_path, mode)
        return cls(file_name, file_handle)

class FileReceivedObj:
    """
    Represents a file received from the UnityPredict platform.

    This class encapsulates information about a file that has been received from
    the UnityPredict platform, including its name and local storage location.

    Attributes:
        FileName (str): The name of the received file.
        LocalFilePath (str): The local path where the file was saved.
    """

    FileName: str = ''
    LocalFilePath: str = ''

    def __init__(self, fileName, localFilePath):
        self.FileName = fileName
        self.LocalFilePath = localFilePath

class IPlatform:
    """
    Interface for UnityPredict platform-specific operations.

    This abstract class defines the set of methods supported by the UnityPredict Platform
    to run operations. 
    """

    __metaclass__ = ABCMeta

    @classmethod
    def version(self): 
        """
        Returns the version of the platform implementation.

        This method allows for version tracking of different platform implementations,
        which is useful for compatibility checking and feature availability.

        Returns:
            str: The version string in semantic versioning format (e.g., "1.0.0").
        """
        return "1.0"

    @abstractmethod
    def getModelsFolderPath(self) -> str: 
        """
        Provides access to the location of model/resource files used for inference.

        This method returns the path to the directory containing all model files and resources
        needed for inference. These files are persistent across requests and should not be modified
        during normal operation.

        Returns:
            str: The absolute path to the models folder.
        """
        raise NotImplementedError

    @abstractmethod
    def getModelFile(self, modelFileName: str, mode: str = 'rb') -> IOBase: 
        """
        Enables loading model/resource files for inference tasks.

        This method provides access to model/resource files by returning a file-like object
        that can be used to read the model/resource data. Model files are persistent across
        requests and should be treated as read-only.

        Args:
            modelFileName (str): The name of the model file to access.
            mode (str, optional): The file open mode. Defaults to 'rb' (read binary).
                Typically, model files should be opened in read mode only.

        Returns:
            IOBase: A file-like object representing the model file.

        Raises:
            FileNotFoundError: If the specified model file doesn't exist.
            IOError: If there's an error opening the file.
        """
        raise NotImplementedError

    @abstractmethod
    def getRequestFile(self, requestFileName: str, mode: str = 'rb', encoding: str = None, errors: str = None, newline: str = None) -> IOBase: 
        """
        Facilitates interaction with request files containing input data.
        
        Request files are input or output files for a particular request to the engine. 
        They are preserved as long as the request is being processed (e.g., when using ReInvokeInSeconds).
        These files are managed by the platform and must be accessed through this method.
        
        This method is used to read input files that were uploaded as part of the request
        or to read output files that were generated by a previous step in the request processing.

        Args:
            requestFileName (str): The name of the request file to access.
            mode (str, optional): The file open mode. Defaults to 'rb' (read binary).
            encoding (str, optional): The encoding to use for text files. Defaults to None (system default).
            errors (str, optional): How to handle encoding errors. Defaults to None (system default).
            newline (str, optional): Controls how universal newlines mode works. Defaults to None (system default).

        Returns:
            IOBase: A file-like object representing the request file.

        Raises:
            FileNotFoundError: If the specified request file doesn't exist.
            IOError: If there's an error opening the file.
        """
        
        raise NotImplementedError

    @abstractmethod
    def saveRequestFile(self, requestFileName: str, mode: str = 'wb', encoding: str = None, errors: str = None, newline: str = None) -> IOBase: 
        """
        Creates or overwrites files on the UnityPredict platform that are associated with the current request.
        
        Request files are input or output files for a particular request to the engine. 
        They are preserved as long as the request is being processed (e.g., when using ReInvokeInSeconds).
        These files are managed by the platform and must be created through this method.
        
        This method is used to create output files that will be returned to the client or
        intermediate files that need to be preserved between steps in the request processing.

        Args:
            requestFileName (str): The name of the request file to create or overwrite.
            mode (str, optional): The file open mode. Defaults to 'wb' (write binary).
                Use 'w' for text files or 'wb' for binary files.
            encoding (str, optional): The encoding to use for text files. Defaults to None (system default).
            errors (str, optional): How to handle encoding errors. Defaults to None (system default).
            newline (str, optional): Controls how universal newlines mode works. Defaults to None (system default).

        Returns:
            IOBase: A file-like object representing the saved file.

        Raises:
            IOError: If there's an error creating or opening the file.
        """
        raise NotImplementedError

    @abstractmethod
    def getRequestFilePublicUrl(self, requestFileName: str) -> str: 
        """
        Retrieves the public URL of a request file that has been uploaded as an input to the UnityPredict platform. 

        Request files are input or output files for a particular request to the engine. 
        They are preserved as long as the request is being processed (e.g., when using ReInvokeInSeconds).
        
        This method is useful when you need to provide a URL to a request file to an external service
        or when you need to make the file accessible via HTTP.

        Args:
            requestFileName (str): The name of the request file.

        Returns:
            str: The public URL of the request file, or None if the file doesn't exist or isn't publicly accessible.
        """
        
        raise NotImplementedError

    @abstractmethod
    def getLocalTempFolderPath(self) -> str: 
        """
        Provides a location for storing temporary files during processing.

        This method returns the path to a directory that can be used for storing temporary files
        during the processing of a request. Files stored in this directory are not preserved
        between requests and should only be used for temporary storage.
        
        For files that need to be preserved between steps in the request processing or returned
        to the client, use the request file methods instead.

        Returns:
            str: The absolute path to the temporary directory.
        """
        
        raise NotImplementedError

    @abstractmethod
    def logMsg(self, msg: str): 
        """
        Enables logging messages on the UnityPredict platform for debugging, monitoring, or informational purposes.

        This method provides a standardized way to log messages that will be captured by the
        UnityPredict platform. These logs can be viewed in the platform's logging interface
        and are useful for debugging, monitoring, and understanding the execution flow.

        Args:
            msg (str): The message to be logged. This should be a descriptive message that
                provides context about what is happening during the execution.
        """
        
        raise NotImplementedError

    @abstractmethod
    def invokeUnityPredictModel(self, modelId: str, request: ChainedInferenceRequest, waitForResponse: bool = True) -> ChainedInferenceResponse: 
        """
        Invokes another UnityPredict model from the current engine, enabling model chaining.

        This method allows the current engine to call another UnityPredict model, passing inputs
        and receiving outputs. This enables complex workflows where multiple models work together,
        with each model specializing in a specific task.
        
        The method handles all the necessary communication with the UnityPredict platform,
        including file transfers, context propagation, and response processing.

        Args:
            modelId (str): The ID of the UnityPredict model to invoke.
            request (ChainedInferenceRequest): A request object containing the inputs and
                desired outcomes for the chained model.
            waitForResponse (bool, optional): If True, the method will wait for the inference to complete
                before returning. If False, it will return immediately with a response containing the
                status URL that can be used to check the inference progress. Defaults to True.

        Returns:
            ChainedInferenceResponse: The response from the chained model, including outcomes,
                errors, and compute costs. If waitForResponse is False and the inference is still
                processing, the response will contain a status URL that can be used to check the
                inference progress. In this case, you can use checkChainedInferenceJobStatus to
                periodically check the status of the inference until it completes.

        Note:
            When waitForResponse is False, you can use checkChainedInferenceJobStatus to poll
            the status of the inference until it completes. The response will contain a status
            URL that can be used with checkChainedInferenceJobStatus to track the progress.
        """
        
        raise NotImplementedError
    
    @abstractmethod
    def checkChainedInferenceJobStatus(self, requestId: str, statusUrl: str = "") -> ChainedInferenceResponse: 
        """
        Checks the status of a previously initiated chained inference job.

        This method is typically called after invokeUnityPredictModel to check the status and retrieve
        results of an asynchronous inference job. It allows for polling the status of long-running
        inference tasks that were initiated through model chaining. When the job is complete,
        this function automatically retrieves and returns all outputs from the completed inference.

        Args:
            requestId (str): The unique identifier of the inference request to check.
                This ID is typically obtained from the response of invokeUnityPredictModel.
            statusUrl (str, optional): The URL to check the status of the inference. If not provided,
                the URL will be constructed using the requestId. Defaults to an empty string.

        Returns:
            ChainedInferenceResponse: The response containing the current status of the inference job,
                including any completed outcomes, error messages, and compute costs. If the job is
                still running, the response may contain partial results or status information.
                When the job is complete, the response will contain all final outputs from the inference.
        """
               
        raise NotImplementedError


# test = ChainedInferenceResponse()
# test.Outcomes = {
#     'outcome': [OutcomeValue('hello', 0)]
# }

# print(test.getOutputValue('outcome'))
from enum import Enum
import json
import attr
from .Platform import VariableInfo, DataTypes

# class OutcomePrediction:
#     Probability = 0.0
#     Value = None

#     def __init__(self):
#         self.Probability = 0.0
#         self.Value = None

# class InputInfo:
#     Name: str = ''
#     InputType: DataTypes = DataTypes.Integer

# class OutcomeInfo:
#     Name: str = ''
#     OutcomeType: DataTypes = DataTypes.Integer
    
# @attr.s(auto_attribs=True)
# class BasePredictEngineConfig:    
#     # Inputs: list[InputInfo] = None
#     # Outcomes: list[OutcomeInfo] = None
#     Inputs: list
#     Outcomes: list

@attr.s(auto_attribs=True)
class InferenceContext:
    ContextId: str = ''
    StoredMeta: dict = {}

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

@attr.s(auto_attribs=True)
class EngineInputs:     
    InputValues: dict
    DesiredOutcomes: list   
    Inputs: dict = {}
    DesiredOutputs: dict = {}
  

class EngineResults:
    Outcomes: dict = {}

    def __init__(self):
        self.Outcomes = dict()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Note: these models will be different for every engine type
###############################################################################################################    
@attr.s(auto_attribs=True)
class AppEngineInferenceOptions:    
    pass

# @attr.s(auto_attribs=True)
# class AIEngineConfiguration (BasePredictEngineConfig):    
#     InferenceOptions: AppEngineInferenceOptions = None

@attr.s(auto_attribs=True)
class AppEngineRequest:    
    RequestId: str = ''
    EngineId: str = ''
    RequestInputFiles: bool = False
    RequestOutputFiles: bool = False
    RequestFilesFolderPath: str = False
    PackagesFolderPath: str = ''
    PackagesFolderPath: str = ''
    SourcesFolderPath: str = ''
    ModelFilesFolderPath: str = ''
    EngineApiKey: str = ''
    PredictEndpoint: str = ''
    LogFilePath: str = ''
    DevLogFilePath: str = ''
    Context: InferenceContext = None
    CallbackQueue: str = ''
    EngineInputData: EngineInputs = None
    # EngineConfig: AIEngineConfiguration = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

###############################################################################################################
    
class UnityPredictEngineResponse:
    RequestId: str = ''
    ErrorMessages: str = ''
    LogMessages: str = ''
    ReInvokeInSeconds: int = -1
    AdditionalInferenceCosts: float = 0.0
    CostToModelUser: float = 0.0
    EngineOutputs: EngineResults = None
    Context: InferenceContext = None

    def __init__(self):
        self.RequestId = ''
        self.ErrorMessages = ''
        self.LogMessages = ''
        self.AdditionalInferenceCosts = 0.0
        self.CostToModelUser = 0.0
        self.ReInvokeInSeconds = 0
        self.EngineOutputs = None
        self.Context = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
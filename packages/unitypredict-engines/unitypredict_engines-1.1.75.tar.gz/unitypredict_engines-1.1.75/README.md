# UnityPredict Local App Engine Creator

## Introduction

The **`unitypredict-engines` python sdk** is designed to help accelerate the testing and debugging of **App Engines** for deployment on the `UnityPredict` platform.

On `UnityPredict`, **"Engines"** are the underlying compute framework that is executed, at scale, to perform inference or run business logic. In contrast, **"Models"** define the interface for these Engines. **Every Engine must be connected to a "Model"** because the Model serves as the interface that defines how `UnityPredict` communicates with the Engine. The Model specifies variable names and data types for inputs and outputs. Additionally, `UnityPredict` uses the Model definition to auto-generate APIs and user interfaces.

**"App Engines"** are specialized extensions of `UnityPredict` Engines that allow developers to write custom Python code, which the platform will execute at scale. These custom-defined Engines offer developers the flexibility needed to create complex applications. Within an App Engine, developers can access various platform features through code. For instance, **App Engine code can easily invoke other models (aka. chaining) or define cost calculations**. App Engines also enable developers to choose specific hardware types for running their code.

This guide focuses on the local development and testing of custom App Engine code.

For a full guide on how to use the UnityPredict Engine features, please visit our complete documentation here: [UnityPredict Docs](https://docs.unitypredict.com).

## Installation
* You can use pip to install the ```unitypredict-engines``` library.
```bash
pip install unitypredict-engines
```

## Usage

TFor detailed instructions on how to use the SDK, please refer to [unitypredict-engines SDK](https://docs.unitypredict.com/sdk).




## License
Copyright 2024 Unified Predictive Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
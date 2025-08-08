
# import logging
# import os
# import re
# import threading
# from datetime import datetime
# from dotenv import load_dotenv

# from .HAIUtils.HAIUtils import (
#     getFrameworkInfo,
#     formatJsonInput,
#     formatJsonExtended,
#     parseJsonInput,
#     formatTypedInput,
#     formatTypedExtended,
#     parseTypedInput,
#     parseInstructions,
#     parseModels,
#     isStructured,
#     safetySettings,
#     extractMediaInfo,
#     getFrames
# )

# load_dotenv()
# logger = logging.getLogger(__name__)

# def isKeySet(envKey):
#     return os.getenv(envKey) is not None

# PROVIDERS = {
#     "OPENAI_API_KEY":    (".HAIConfigs.OpenAIConfig",   "OpenAIConfig",   "openai"),
#     "ANTHROPIC_API_KEY": (".HAIConfigs.AnthropicConfig","AnthropicConfig","anthropic"),
#     "GOOGLE_API_KEY":    (".HAIConfigs.GoogleConfig",   "GoogleConfig",   "google"),
#     "GROQ_API_KEY":      (".HAIConfigs.GroqConfig",     "GroqConfig",     "groq"),
# }

# providerMap = {}

# for key, (module, clsName, mapKey) in PROVIDERS.items():
#     if isKeySet(key):
#         try:
#             mod = __import__(module, fromlist=[clsName])
#             providerMap[mapKey] = getattr(mod, clsName)()
#         except ImportError as e:
#             # Optionally log or warn here
#             pass

import logging
import os
import re
import threading
from importlib import import_module
from datetime import datetime
from dotenv import load_dotenv

from .HAIUtils.HAIUtils import (
    getFrameworkInfo,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    parseInstructions,
    parseModels,
    isStructured,
    safetySettings,
    extractMediaInfo,
    getFrames
)

load_dotenv()
logger = logging.getLogger(__name__)

def setProvider(apiInput=None):
    """
    Sets provider API keys from string, tuple, or list, or env.
    Passes API key directly to config if possible.
    Returns a providerMap of all found providers.
    """

    PROVIDERS = {
        "OPENAI_API_KEY":    ("HoloAI.HAIConfigs.OpenAIConfig",   "OpenAIConfig",   "openai"),
        "ANTHROPIC_API_KEY": ("HoloAI.HAIConfigs.AnthropicConfig","AnthropicConfig","anthropic"),
        "GOOGLE_API_KEY":    ("HoloAI.HAIConfigs.GoogleConfig",   "GoogleConfig",   "google"),
        "GROQ_API_KEY":      ("HoloAI.HAIConfigs.GroqConfig",     "GroqConfig",     "groq"),
        "XAI_API_KEY":       ("HoloAI.HAIConfigs.xAIConfig",      "xAIConfig",      "xai"),
    }


    # Step 1: Parse keys from apiInput (if given) and always set env too (for backward compat)
    keyMap = {}
    if apiInput is None:
        inputList = []
    elif isinstance(apiInput, str):
        inputList = [apiInput.strip()]
    elif isinstance(apiInput, (list, tuple)):
        inputList = [s.strip() for s in apiInput if isinstance(s, str) and s.strip()]
    else:
        raise ValueError("setProvider input must be a string, list, tuple, or None")

    for assignment in inputList:
        try:
            envKey, apiKey = assignment.split('=', 1)
            envKey = envKey.strip()
            apiKey = apiKey.strip()
            os.environ[envKey] = apiKey  # set for backward compat
            keyMap[envKey] = apiKey      # track for direct pass
        except Exception:
            raise ValueError(f"Each assignment must be 'PROVIDER_KEY=key', got: {assignment}")

    providerMap = {}
    for envKey, (module, clsName, mapKey) in PROVIDERS.items():
        apiKey = keyMap.get(envKey) or os.getenv(envKey)
        if apiKey:
            try:
                mod = import_module(module)
                # Pass apiKey directly if config supports it, else fallback to no-arg
                try:
                    providerMap[mapKey] = getattr(mod, clsName)(apiKey)
                except TypeError:
                    providerMap[mapKey] = getattr(mod, clsName)()
            except ImportError:
                continue

    return providerMap

MODELS = {
    ("gpt", "o"): "openai",
    ("claude",): "anthropic",
    ("llama", "meta-llama", "gemma2", "qwen", "deepseek",): "groq",
    ("gemini", "gemma",): "google",
    ("grok"): "xai",
}


class HoloAI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloAI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.providerMap = setProvider()

        self.initialized = True

    def getFrameworkInfo(self):
        """
        Returns a string with framework information.
        """
        return getFrameworkInfo()

    def listProviders(self):
        """
        Returns a list of available model providers.
        This is based on the keys of the providerMap dictionary.
        """
        return list(self.providerMap.keys())

    def setProvider(self, apiInput=None):
        """
        Sets provider API keys from:
        - a single string:      'PROVIDER_KEY=api_key'
        - a tuple of strings:   ('PROVIDER_KEY=api_key', ...)
        - a list of strings:    ['PROVIDER_KEY=api_key', ...]
        - or uses environment if nothing passed.

        Returns a providerMap of all found providers.
        """
        self.providerMap = setProvider(apiInput)

    def _inferModelProvider(self, model: str):
        """
        Infers the provider based on the model name.
        Returns the provider name as a string, or None if not found.
        """
        return next(
            (provider for prefixes, provider in MODELS.items()
             if any(model.startswith(prefix) for prefix in prefixes)),
            None
        )

    def _getProviderConfig(self, model: str):
        """
        Returns the config instance strictly based on model's inferred provider.
        Raises if provider cannot be inferred.
        """
        provider = self._inferModelProvider(model)
        if provider and provider in self.providerMap:
            return self.providerMap[provider]
        raise ValueError(f"Cannot infer provider from model '{model}'. Valid providers: {list(self.providerMap.keys())}")

    def HoloCompletion(self, **kwargs):
        """
        HoloAI completion requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills and actions to use (Optional) [skills, actions].
            - tools: (list) Tools to use (Optional) [tools].
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision object if image paths are found.
        """
        return self._routeCompletion(**kwargs)

    def HoloAgent(self, **kwargs):
        """
        HoloAI agent requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: (list) Skills and actions to use (Optional) [skills, actions].
            - tools: (list) Tools to use (Optional) [tools].
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision object if image paths are found.
        """
        return self._routeCompletion(**kwargs)

    def Reasoning(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Response(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Vision(self, **kwargs):
        """
        Get a Vision response from the Vision model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - files: (list) List of image file paths (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        return self._routeVision(**kwargs)

    def Agent(self, **kwargs):
        """
        Get a Response from the Agent model.
        :param kwargs: Keyword arguments to customize the request.
            - task: (str) Task type ('response', 'reasoning', 'vision') (Optional (default: 'response')).
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tools: (list) Tools to use (Optional) [tools].
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Reasoning, Response, or Vision object.
        """
        #return self._routeResponse(**kwargs)
        task = kwargs.get('task', 'response').lower()
        taskMap = {
            'reasoning': self._routeResponse,
            'response': self._routeResponse,
            'vision': self._routeVision,
        }
        if task not in taskMap:
            raise ValueError(f"Unknown task: '{task}'. Supported tasks: {list(taskMap.keys())}")
        return taskMap[task](**kwargs)

    #------------- Utility Methods -------------#
    def _routeCompletion(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        models  = kwargs.get("models") or kwargs.get("model")
        raw     = kwargs.get("input") or kwargs.get("user")
        system  = parseInstructions(kwargs)
        verbose = kwargs.get("verbose", False)
        if models is None or raw is None:
            raise ValueError("HoloCompletion requires 'model' or 'models' and input/user")

        models = parseModels(models)

        # 1. Normalize user input
        if isinstance(raw, list):
            last = raw[-1]
            text = last["content"] if isinstance(last, dict) and "content" in last else str(last)
        else:
            text = str(raw)

        # 2. Detect mode
        images = extractMediaInfo(text)

        # 3. Select mode
        def visionMode():
            img = images[-1]
            promptOnly = re.split(re.escape(img), text)[0].strip()
            return self.Vision(
                model=models['vision'],
                system=system,
                user=promptOnly,
                files=images,
                collect=5,
                verbose=verbose
            )

        def responseMode():
            kwargs['model'] = models['response']
            return self.Response(**kwargs)

        modeMap = {
            "vision": visionMode,
            "response": responseMode,
            # Add more modes here, e.g., "audio": audioMode, etc.
        }

        mode = "vision" if images else "response"
        return modeMap[mode]()

    def _routeResponse(self, **kwargs):
        #print(f"\n[Response Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        return config.getResponse(**kwargs)

    def _routeVision(self, **kwargs):
        #print(f"\n[Vision Request] {kwargs}")
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.get('model')
        config = self._getProviderConfig(model)
        notice = kwargs.get('paths')
        if notice:
            print(f"[Notice] 'paths' is being deprecated in future releases, please use 'files' instead.")
        return config.getVision( **kwargs)

    def isStructured(self, obj):
        """
        Check if the input is a structured list of message dicts.
        A structured list is defined as a list of dictionaries where each dictionary
        contains both "role" and "content" keys.
        Returns True if the input is a structured list, False otherwise.
        """
        return isStructured(obj)

    def formatInput(self, value):
        """
        Formats the input value into a list.
        - If `value` is a string, returns a list containing that string.
        - If `value` is already a list, returns it as is.
        - If `value` is None, returns an empty list.
        """
        return [value] if isinstance(value, str) else value

    def formatConversation(self, convo, user):
        """
        Returns a flat list representing the full conversation:
        - If `convo` is a list, appends the user input (str or list) to it.
        - If `convo` is a string, creates a new list with convo and user input.
        """
        if isinstance(convo, str):
            convo = [convo]
        if isinstance(user, str):
            return convo + [user]
        elif isinstance(user, list):
            return convo + user
        else:
            raise TypeError("User input must be a string or list of strings.")


    def formatJsonInput(self, role: str, content: str) -> dict:
        """
        Format content for JSON-based APIs like OpenAI, Groq, etc.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatJsonInput(role=role, content=content)

    def formatJsonExtended(self, role: str, content: str) -> dict:
        """
        Extended JSON format for APIs like OpenAI, Groq, etc.
        Maps 'assistant', 'developer', 'model' and 'system' to 'assistant'.
        All other roles (including 'user') map to 'user'.
        """
        return formatJsonExtended(role=role, content=content)

    def parseJsonInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized message objects using formatJsonExtended.
        """
        return parseJsonInput(data)

    def formatTypedInput(self, role: str, content: str) -> dict:
        """
        Format content for typed APIs like Google GenAI.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatTypedInput(role=role, content=content)

    def formatTypedExtended(self, role: str, content: str) -> dict:
        """
        Extended typed format for Google GenAI APIs.
        Maps 'assistant', 'developer', 'system' and 'model' to 'model'.
        All other roles (including 'user') map to 'user'.
        """
        return formatTypedExtended(role=role, content=content)

    def parseTypedInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized Google GenAI message objects using formatTypedExtended.
        """
        return parseTypedInput(data)

    def safetySettings(self, **kwargs):
        """
        Construct a list of Google GenAI SafetySetting objects.

        Accepts thresholds as keyword arguments:
            harassment, hateSpeech, sexuallyExplicit, dangerousContent

        Example:
            safetySettings(harassment="block_high", hateSpeech="block_low")
        """
        return safetySettings(**kwargs)

    def extractMediaInfo(self, text: str):
        """
        Extracts image file paths from a given text.
        Supports both Windows and Unix-style paths.
        Returns a list of matched image paths.
        """
        return extractMediaInfo(text)

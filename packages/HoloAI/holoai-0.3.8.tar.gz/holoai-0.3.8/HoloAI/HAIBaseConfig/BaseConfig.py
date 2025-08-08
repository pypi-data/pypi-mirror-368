import os
import threading
from SkillLink import SkillLink

from HoloAI.HAIUtils.HAIUtils import (
    parseInstructions,
    validateResponseArgs,
    validateVisionArgs,
    safeStrip,
)


class BaseConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(BaseConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.skillLink = SkillLink()  # Initialize the SkillLink instance
        self.skills  = None
        self.tools   = None
        self.show    = 'hidden'
        self.effort  = 'auto'
        self.budget  = 1369
        self.tokens  = 3369
        self.files   = []      # Default paths for images
        self.collect = 10      # Default number of frames to collect
        self.verbose = False
        self.choice  = 'auto'  # Default choice for tool choice

        self.initialized = True

    # ---------------------------------------------------------
    # Public methods
    # ---------------------------------------------------------
    def getResponse(self, **kwargs):
        """
        Get a Response from the configured model.
        """
        user = kwargs.get('user') or kwargs.get('input')
        if user is not None:
            kwargs['user'] = user
        system = parseInstructions(kwargs)
        if system is not None:
            kwargs['system'] = system
        if 'tokens' not in kwargs and 'max_tokens' in kwargs:
            kwargs['tokens'] = kwargs['max_tokens']
        if 'budget' not in kwargs and 'max_budget' in kwargs:
            kwargs['budget'] = kwargs['max_budget']
        if 'files' not in kwargs and 'paths' in kwargs:
            kwargs['files'] = kwargs['paths']
        if 'choice' not in kwargs and 'tool_choice' in kwargs:
            kwargs['choice'] = kwargs['tool_choice']
        # keys = [
        #     "model", "system", "user", "skills", "tools", "choice",
        #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
        # ]
        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)
        validateResponseArgs(params["model"], params["user"])
        return self.Response(**params)

    def getVision(self, **kwargs):
        """
        Get a Vision response from the configured model.
        """
        user = kwargs.get('user') or kwargs.get('input')
        if user is not None:
            kwargs['user'] = user
        system = parseInstructions(kwargs)
        if system is not None:
            kwargs['system'] = system
        if 'tokens' not in kwargs and 'max_tokens' in kwargs:
            kwargs['tokens'] = kwargs['max_tokens']
        if 'budget' not in kwargs and 'max_budget' in kwargs:
            kwargs['budget'] = kwargs['max_budget']
        if 'files' not in kwargs and 'paths' in kwargs:
            kwargs['files'] = kwargs['paths']
        if 'choice' not in kwargs and 'tool_choice' in kwargs:
            kwargs['choice'] = kwargs['tool_choice']
        # keys = [
        #     "model", "system", "user", "skills", "tools", "choice",
        #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
        # ]
        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)
        validateVisionArgs(params["model"], params["user"], params["files"])
        return self.Vision(**params)

    def getKeys(self, key):
        keyMap = {
            "response": [
                "model", "system", "user", "skills", "tools", "choice",
                "show", "effort", "budget", "tokens", "files", "verbose"
            ],
            "vision": [
                "model", "system", "user", "skills", "tools", "choice",
                "show", "effort", "budget", "tokens", "files", "collect", "verbose"
            ]
        }
        try:
            return keyMap[key.lower()]
        except KeyError:
            raise ValueError(f"Unknown key set: {key}")

    def extractKwargs(self, kwargs, keys, defaults=None):
        """
        Extracts specified keys from kwargs, using defaults or class attributes if needed.

        Args:
            kwargs (dict): Incoming keyword arguments.
            keys (list[str]): Keys to extract.
            defaults (dict, optional): Default values for keys.

        Returns:
            dict: Extracted key-value pairs.
        """
        result = {}
        defaults = defaults or {}
        for k in keys:
            # Priority: kwargs > defaults > class attribute > None
            result[k] = kwargs.get(k,
                           defaults.get(k, getattr(self, k, None)))
        return result

    def extractIntent(self, user):
        """
        Extract the last user text from a string, a list of message dicts, or a mixed list.
        Returns a string suitable for use in skills or message formatting.
        """
        # if isinstance(user, list) and user:
        #     lastMsg = user[-1]
        #     if isinstance(lastMsg, dict):
        #         content = lastMsg.get("content", "")
        #         # If content is a list of type-objects (OpenAI v1)
        #         if isinstance(content, list):
        #             return " ".join(
        #                 str(part.get("text", "")) for part in content if part.get("type") == "text"
        #             ).strip()
        #         # If content is a string (Anthropic etc.)
        #         if isinstance(content, str):
        #             return content.strip() if content else ""
        #         # Fallback: convert to string if not None, else empty
        #         return str(content).strip() if content is not None else ""
        #     if isinstance(lastMsg, str):
        #         return lastMsg.strip() if lastMsg else ""
        #     return str(lastMsg).strip() if lastMsg is not None else ""
        # elif isinstance(user, str):
        #     return user.strip() if user else ""
        # return ""
        if isinstance(user, list) and user:
            lastMsg = user[-1]
            if isinstance(lastMsg, dict):
                content = lastMsg.get("content", "")
                if isinstance(content, list):
                    return " ".join(
                        safeStrip(part.get("text", "")) for part in content if part.get("type") == "text"
                    )
                if isinstance(content, str):
                    return safeStrip(content)
                return safeStrip(content)
            if isinstance(lastMsg, str):
                return safeStrip(lastMsg)
            return safeStrip(lastMsg)
        elif isinstance(user, str):
            return safeStrip(user)
        return ""

    def skillInstructions(self, capabilities):
        """
        Get skill instructions for the ava based on its capabilities.
        NOTE: the skillInstructions in the skillLink method will automatically use your naming conventions you can also,
        - pass limit=(int e.g 10) to limit the number of examples included in the instructions, or
        - pass verbose=True to view the instructions in detail as it will print the instructions to the console.
        """
        return self.skillLink.skillInstructions(capabilities)

    def getActions(self, action: str) -> list:
        """
        Get a list of actions based on the given action string.
        This method uses the skills manager's action parser to retrieve actions that match the given string.
        If the action is not found, it returns an empty list.
        """
        return self.skillLink.actionParser.getActions(action)

    def executeActions(self, actions, action):
        """
        Execute a list of actions using the skillLink's executeActions method.
        This method will return the results of the executed actions.
        If the actions are not found, it will return an empty list.
        """
        return self.skillLink.executeActions(actions, action)

    def executeSkills(self, skills, user, tokens, verbose=False) -> str:
        """
        Execute skills based on the provided skills, user input, and tokens.
        This method processes the skills, retrieves the actions, and executes them.
        :param skills: List of skills to execute.
        :param user: User input to provide context for the skills.
        :param tokens: Number of tokens to use for the skills execution.
        :param verbose: If True, prints detailed information about the execution.
        :return: A string containing the results of the executed skills.
        """
        if skills:
            agentSkills, actions = (skills or [None, None])[:2]
            instructions  = self.skillInstructions(agentSkills)
            calledActions = self.processSkills(instructions, user, tokens)
            getActions    = self.getActions(calledActions)
            if getActions:
                results         = self.executeActions(actions, getActions)
                filteredResults = [str(result) for result in results if result]
                if filteredResults:
                    combined = "\n".join(filteredResults)
                    if verbose:
                        print(f"Combined Results:\n{combined}\n")
                    return f"Use these results from the actions called when responding:\n{combined}"
        return 'None'
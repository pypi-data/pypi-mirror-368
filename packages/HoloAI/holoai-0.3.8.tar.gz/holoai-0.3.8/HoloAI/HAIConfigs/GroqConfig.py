import os
import threading
from dotenv import load_dotenv
from groq import Groq

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames,
    supportsReasoning,
    extractFileInfo,
    extractText
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()

class GroqConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("GROQ_API_KEY")
        if not apiKey:
            raise KeyError("Groq API key not found. Please set GROQ_API_KEY in your environment variables.")
        self.client = Groq(api_key=apiKey)

    def _setModels(self):
        self.RModel = os.getenv("GROQ_RESPONSE_MODEL", "llama-3.1-8b-instant")
        self.VModel = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        # keys = [
        #     "model", "system", "user", "skills", "tools", "choice",
        #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
        # ]
        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)

        messages = []
        messages.append(formatJsonInput("system", params["system"]))
        messages.extend(parseJsonInput(params["user"]))

        args = self._getArgs(params["model"], messages, params["tokens"])

        if params["tools"]:
            args["tools"] = params["tools"]
            #args["tool_choice"] = params["choice"]
            args["tool_choice"] = self._mapChoice(params.get("choice"))

        if params["skills"]:
            additionalInfo = self.executeSkills(params["skills"], params["user"], params["tokens"], params["verbose"])
            if additionalInfo:
                messages.append(formatJsonInput("user", additionalInfo))

        # intent = self.extractIntent(params["user"])
        # fileInfo = extractFileInfo(intent)
        # if fileInfo:
        #     messages.append(formatJsonInput("user", fileInfo))

        # files = params["files"]
        # if files:
        #     fileInfo = str(extractText(files))
        #     if fileInfo:
        #         messages.append(formatJsonInput("user", fileInfo))
        messages += self._DocFiles(params)

        if supportsReasoning(params["model"]):
            args["reasoning_format"] = params["show"]  # "parsed", "raw", or "hidden"
            if params["model"].startswith("qwen/qwen3-32b"):
                args["reasoning_effort"] = "default"
            if params["effort"] == "auto":
                params["budget"] = 1024
                args["max_completion_tokens"] = params["budget"]

        response = self._endPoint(**args)# self.client.chat.completions.create(**args)
        return response if params["verbose"] else response.choices[0].message.content

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        # keys = [
        #     "model", "system", "user", "skills", "tools", "choice",
        #     "show", "effort", "budget", "tokens", "files", "collect", "verbose"
        # ]
        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)

        messages = []

        images = self._mediaFiles(params["files"], params["collect"])

        userContent = [{"type": "text", "text": params["user"]}] + images
        payload = messages.copy()
        payload.append({
            "role": "user",
            "content": userContent
        })

        args = self._getArgs(params["model"], payload, params["tokens"])

        response = self._endPoint(**args)# self.client.chat.completions.create(**args)
        return response if params["verbose"] else response.choices[0].message.content

    def processSkills(self, instructions, user, tokens) -> str:
        messages = []
        messages.append(formatJsonInput("system", instructions))
        intent = self.extractIntent(user)
        messages.append(formatJsonInput("user", intent))
        args = self._getArgs(self.RModel, messages, tokens)
        response= self._endPoint(**args)# self.client.chat.completions.create(**args)
        return response.choices[0].message.content

    def _endPoint(self, **args):
        return self.client.chat.completions.create(**args)

    def _getArgs(self, model, messages, tokens):
        args = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": tokens,
        }
        return args

    def _mapChoice(self, choice):
        mapping = {
            "auto": "auto",
            "required": "required",
            "none": "none"
        }
        return mapping[(choice or "auto").lower()]

    def _mediaFiles(self, files, collect):
        images = []
        for path in files:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
            })
        return images

    def _DocFiles(self, params):
        messages = []
        intent = self.extractIntent(params["user"])
        fileInfo = extractFileInfo(intent)
        if fileInfo:
            messages.append(formatJsonInput("user", fileInfo))
        files = params["files"]
        if files:
            fileInfo = str(extractText(files))
            if fileInfo:
                messages.append(formatJsonInput("user", fileInfo))
        return messages

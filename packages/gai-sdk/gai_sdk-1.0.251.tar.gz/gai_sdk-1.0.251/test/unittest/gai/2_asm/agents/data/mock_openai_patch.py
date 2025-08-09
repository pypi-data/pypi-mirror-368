import os
import json
from pydantic import TypeAdapter
from typing import List
# Gai imports
from gai.llm.openai.types import ChatCompletionChunk, ChatCompletion
# Ollama imports
from ollama import ChatResponse
# Anthropic imports
from anthropic.types import MessageStreamEvent


here = os.path.abspath(os.path.dirname(__file__))


def chat_completions_generate(client_type):

    # Load openai output

    if client_type == "openai":
        filename = "1a_generate_text_openai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatCompletion(**jsoned)
        return completion

    # Load ollama output

    if client_type == "ollama":
        filename = "2a_generate_text_ollama.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
        return ChatResponse(**jsoned)

    # Load gai output

    if client_type == "gai":
        filename = "3a_generate_text_gai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
        return ChatCompletion(**jsoned)

    # Load anthropic output
    if client_type == "anthropic":
        filename = "4a_generate_text_anthropic.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
        from anthropic.types import Message
        from pydantic import TypeAdapter
        adapter = TypeAdapter(Message)
        content = adapter.validate_python(jsoned)
        return content


def chat_completions_stream(client_type):
    def streamer():
        if client_type == "openai":
            filename = "1b_stream_text_openai.json"
            fullpath = os.path.join(here, filename)
            with open(fullpath, "r") as f:
                list = json.load(f)
                for chunk in list:
                    chunk = ChatCompletionChunk(**chunk)
                    chunk.extract = lambda: chunk.choices[0].delta.content
                    yield chunk

        elif client_type == "ollama":
            filename = "2b_stream_text_ollama.json"
            fullpath = os.path.join(here, filename)
            with open(fullpath, "r") as f:
                list = json.load(f)
                for chunk in list:
                    chunk = ChatResponse(**chunk)
                    chunk.extract = lambda: chunk.message.content
                    yield chunk

        elif client_type == "gai":
            filename = "3b_stream_text_gai.json"
            fullpath = os.path.join(here, filename)
            with open(fullpath, "r") as f:
                list = json.load(f)
                for chunk in list:
                    chunk = ChatCompletionChunk(**chunk)
                    chunk.extract = lambda: chunk.choices[0].delta.content
                    yield chunk

        elif client_type == "anthropic":
            filename = "4b_stream_text_anthropic.json"
            fullpath = os.path.join(here, filename)
            with open(fullpath, "r") as f:
                chunks = json.load(f)
                adapter = TypeAdapter(List[MessageStreamEvent])
                chunks = adapter.validate_python(chunks)
                for chunk in chunks:
                    yield chunk
        else:
            raise ValueError(f"Unknown client type: {client_type}")

    return (chunk for chunk in streamer())


def chat_completions_toolcall(client_type):

    if client_type == "openai":
        filename = "1c_toolcall_openai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatCompletion(**jsoned)
        return completion

    if client_type == "ollama":
        filename = "2c_toolcall_ollama.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatResponse(**jsoned)
        return completion

    if client_type == "gai":
        filename = "3c_toolcall_gai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatCompletion(**jsoned)
        return completion

    raise ValueError(f"Unknown client type: {client_type}")


def chat_completions_streaming_toolcall(client_type):

    def streamer():
        if client_type == "anthropic":
            filename = "4c_stream_tool_anthropic.json"
            fullpath = os.path.join(here, filename)
            with open(fullpath, "r") as f:
                chunks = json.load(f)
                adapter = TypeAdapter(List[MessageStreamEvent])
                chunks = adapter.validate_python(chunks)
                for chunk in chunks:
                    yield chunk
        else:
            raise ValueError(f"Unknown client type: {client_type}")

    return (chunk for chunk in streamer())


def chat_completions_jsonschema(client_type):
    if client_type == "openai":
        filename = "1d_jsonschema_openai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatCompletion(**jsoned)
        return completion

    if client_type == "ollama":
        filename = "2d_jsonschema_ollama.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatResponse(**jsoned)
        return completion

    if client_type == "gai":
        filename = "3d_jsonschema_gai.json"
        fullpath = os.path.join(here, filename)
        with open(fullpath, "r") as f:
            jsoned = json.load(f)
            completion = ChatCompletion(**jsoned)
        return completion

    raise ValueError(f"Unknown client type: {client_type}")

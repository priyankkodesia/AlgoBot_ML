import functools
import os
import typing as t
import logging as logger
import boto3
import json

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src._types import Message, Parameters, Role, ChatFunction

from openai import OpenAI

from openai import OpenAI
import typing as t
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def chat_openai(messages: t.List[Message], parameters: Parameters) -> Message:
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Prepare messages in the required format for OpenAI
    formatted_messages = [{"role": message.role, "content": message.content} for message in messages]

    # Send messages to OpenAI API
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=formatted_messages,
        temperature=parameters.temperature,
        max_tokens=parameters.max_tokens,
        top_p=parameters.top_p,
    )

    # Extract the response message from choices
    response_message = chat_completion.choices[0].message

    # Log information if needed
    logger.info(f'Model: gpt-3.5-turbo\nMessages: {formatted_messages}\nOutputMessage: {response_message}')

    # Return the response message
    return Message(role="assistant", content=response_message['content'])


def chat_mistral(
        messages: t.List[Message], parameters: Parameters
) -> Message:
    client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
    messages = [
        ChatMessage(role=message.role, content=message.content) for message in messages
    ]

    response = client.chat(
        model=parameters.model,
        messages=messages,
        temperature=parameters.temperature,
        max_tokens=parameters.max_tokens,
        top_p=parameters.top_p,
    )
    response_message = response.choices[-1].message
    logger.info(f'Model: {parameters.model}\nMessages: {messages}\nOutputMessage: {response_message}')
    return Message(role=response_message.role, content=response_message.content)


def chat_bedrock(messages: t.List[Message], parameters: Parameters) -> Message:
    bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
    """
    Sends a message to a model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The model ID to use.
        system_text (JSON) : The system prompt.
        input text : The input message.

    Returns:
        response (JSON): The conversation that the model generated.

    """

    logger.debug("Generating message with model %s", parameters.model)

    bedrock_messages = [{"role": message.role.value, "content": [{"text": message.content}]} for message in messages if
                        message.role != 'system']

    system_prompt_exists = any([message.content for message in messages if message.role == 'system'])
    system_prompts = [{"text": next((message.content for message in messages if message.role == 'system'), None)}]

    # Base inference parameters to use.
    inference_config = {"temperature": parameters.temperature,
                        "topP": parameters.top_p,
                        "maxTokens": parameters.max_tokens
                        }
    # Additional inference parameters to use.
    # additional_model_fields = {"top_k": top_k}

    # Send the message.
    if system_prompt_exists:
        response = bedrock_client.converse(
            modelId=parameters.model,
            messages=bedrock_messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            # additionalModelRequestFields=additional_model_fields
        )
    else:
        response = bedrock_client.converse(
            modelId=parameters.model,
            messages=bedrock_messages,
            # system=system_prompts,
            inferenceConfig=inference_config,
            # additionalModelRequestFields=additional_model_fields
        )
    output_message = response['output']['message']
    content = ' '.join(bedrock_content_dict['text'] for bedrock_content_dict in output_message['content'])
    logger.debug(f'Model: {parameters.model}\nMessages: {messages}\nOutputMessage: {content}')
    return Message(role=output_message['role'], content=content)


def agent_setup(agent_model: str,
                agent_temp: float = 0.3,
                agent_top_p: float = 1.0,
                agent_max_tokens: int = 1024):
    agent_func, agent_model = Models[agent_model]

    agent_chat = t.cast(
        ChatFunction,
        functools.partial(
            agent_func,
            parameters=Parameters(
                model=agent_model,
                temperature=agent_temp,
                top_p=agent_top_p,
                max_tokens=agent_max_tokens,
            ),
        ),
    )
    return agent_chat


def convert_http_to_python_request_with_mistral(http_request,
                                                model="mistral.mistral-large-2402-v1:0",
                                                temperature=0.5,
                                                top_p=1.0,
                                                max_tokens=1024
                                                ):
    http_convert_message = Message(
        role=Role('user'), content=str('Convert this HTTP to a python request \n' + http_request)
    )
    parameters = Parameters(
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )

    return chat_bedrock([http_convert_message], parameters)


Models: t.Dict[str, t.Tuple] = {
    "gpt-3.5": (chat_openai, "gpt-3.5-turbo"),
    # "gpt-3.5": (chat_openai, "gpt-3.5-turbo-instruct"),
    # "gpt-4": (chat_openai, "gpt-4"),
    "gpt-4-turbo": (chat_openai, "gpt-4-1106-preview"),
    # "llama-13b": (chat_together, "togethercomputer/llama-2-13b-chat"),
    # "llama-70b": (chat_together, "togethercomputer/llama-2-70b-chat"),
    # "vicuna-13b": (chat_together, "lmsys/vicuna-13b-v1.5"),
    # "mistral-small-together": (chat_together, "mistralai/Mixtral-8x7B-Instruct-v0.1"),
    # "mistral-medium": (chat_mistral, "mistral-medium-latest"),
    # "mistral-small": (chat_mistral, "mistral-small-latest"),
    # "mistral-large_": (chat_mistral, "mistral-large-latest"),
    # "mixtral-8x7b": (chat_mistral, "open-mixtral-8x7b"),
    # "mistral-7b": (chat_mistral, "open-mistral-7b"),
    "llama2-13b": (chat_bedrock, "meta.llama2-13b-v1"),
    "llama2-70b": (chat_bedrock, "meta.llama2-70b-v1"),
    "llama2-chat-13b": (chat_bedrock, "meta.llama2-13b-chat-v1"),
    "llama2-chat-70b": (chat_bedrock, "meta.llama2-70b-chat-v1"),
    "llama3-8b-instruct": (chat_bedrock, "meta.llama3-8b-instruct-v1:0"),
    "llama3-70b-instruct": (chat_bedrock, "meta.llama3-70b-instruct-v1:0"),
    "mistral-small": (chat_bedrock, "mistral.mistral-small-2402-v1:0"),
    "mistral-large": (chat_mistral, "mistral.mistral-large-2402-v1:0"),
    "aws-titan-text-express": (chat_bedrock, "amazon.titan-text-express-v1"),
    "aws-titan-text-lite": (chat_bedrock, "amazon.titan-text-lite-v1"),
    "aws-titan-text-premier": (chat_bedrock, "amazon.titan-text-premier-v1:0"),
    "mixtral-8x7b-instruct": (chat_bedrock, "mistral.mixtral-8x7b-instruct-v0:1"),
    "mistral-7b-instruct": (chat_bedrock, "mistral.mistral-7b-instruct-v0:2"),
    "ai21-labs-Jurassic-2-Mid": (chat_bedrock, "ai21.j2-mid-v1"),
    "ai21-labs-Jurassic-2-Ultra": (chat_bedrock, "ai21.j2-ultra-v1"),
    "cohere-command": (chat_bedrock, "cohere.command-text-v14"),
    "cohere-command-light": (chat_bedrock, "cohere.command-light-text-v14"),
    "cohere-command-r": (chat_bedrock, "cohere.command-r-v1:0"),
    "cohere-command-r-plus": (chat_bedrock, "cohere.command-r-plus-v1:0"),
    "Claude": (chat_bedrock, "anthropic.claude-v2:1"),
    "Claude 3 Sonnet": (chat_bedrock, "anthropic.claude-3-sonnet-20240229-v1:0"),
    "Claude 3 Haiku": (chat_bedrock, "anthropic.claude-3-haiku-20240307-v1:0"),
    "Claude 3 Opus": (chat_bedrock, "anthropic.claude-3-opus-20240229-v1:0"),
    "Claude Instant": (chat_bedrock, "anthropic.claude-instant-v1"),
}

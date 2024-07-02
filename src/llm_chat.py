import logging as logger

from src._types import Message, Role
from src.models import agent_setup


def process_chat(prompt):
    chat = agent_setup(agent_model="gpt-3.5", agent_temp=1.0, agent_top_p=0.9, agent_max_tokens=512)

    logger.info(f"Chat object type: {type(chat)}")
    logger.info(f"Chat object methods: {dir(chat)}")

    # Create the chat messages list
    messages = [# Uncomment and customize the system prompt if needed
        # Message(role=Role.system, content="system_prompt"),
        Message(role=Role.user, content=prompt), ]

    # Process the chat and return the response content
    response = chat(messages)
    return response.content

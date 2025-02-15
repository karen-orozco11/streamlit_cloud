from openai import OpenAI
from logger import Logger

class OpenAIHelper:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        Logger.log_success("OpenAIHelper initialized")

    def compose_chat_messages(self, conversation_history):
        messages = []
        for entry in conversation_history:
            role = "assistant" if entry['role'] == 'adviser' else entry['role']
            messages.append({
                "role": role,
                "content": entry['text']
            })
        Logger.log_success(f"Composed chat messages from conversation history:\n {messages}")
        return messages

    def get_response(self, question, conversation_history):
        try:
            messages = self.compose_chat_messages(conversation_history)
            messages.append({"role": "user", "content": question})
            Logger.log_info(f"Sending messages to OpenAI: {messages}")

            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            response_content = completion.choices[0].message.content
            Logger.log_success(f"Received response from OpenAI: {response_content}")
            return response_content
        except Exception as e:
            Logger.log_error(e)
            raise 
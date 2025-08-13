

from datetime import datetime
import json

import requests
from castleguard_sdk.castleguard_base import CastleGuardBase


class Chat(CastleGuardBase):

    def chat(self, prompt, chat_id=None, collection_id=None, expert_ids=None, model="default", store_in_db=True):
        """
        Interacts with the chat endpoint to generate a response from the model.

        :param prompt: The input prompt to send to the model.
        :param chat_id: Optional chat session ID.
        :param collection_id : int | Iterable[int] | Sequence[int] | None, optional
        :param expert_ids: int | Iterable[int] | Sequence[int] | None, optional
        :return: Chatbot response or 'Unknown' if the request fails.
        """

        collection_id_list = self.normalize_to_list(collection_id, int)
        expert_id_list = self.normalize_to_list(expert_ids, int)
        print("collection_id_list", collection_id_list)
        if chat_id is None:
            chat_id = 0
        return self.send_message_to_chat(chat_id, prompt, collection_id_list, expert_id_list, model, store_in_db)

    def chat_with_collection(self, prompt, collection_id=None):
        """
        Interacts with the chat endpoint to generate a response from the model.

        :param prompt: The input prompt to send to the model.
        :param chat_id: Optional chat session ID.
        :return: Chatbot response or 'Unknown' if the request fails.
        """

        # create a new chat session
        chat_id = self.create_chat()
        if chat_id is None:
            return "", None

        return self.send_message_to_chat(chat_id, prompt, [collection_id], [], "default", True)

    def create_chat(self):

        url = self.get_url('chat-completion/chat')
        headers = self.get_headers()

        params = {
            "displayName": "Chat " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        chat_response = requests.post(url, headers=headers, params=params)
        if chat_response.status_code == 200:
            return json.loads(chat_response.text).get('id')
        else:
            self.log("Failed to create chat session", logLevel=3)
            self.log(f"Error: {chat_response.text} statuse{chat_response.status_code}", logLevel=3)
            return None

    def send_message_to_chat(self, chat_id, prompt, collection_ids=[], expert_ids=[], model="default", store_in_db=True):

        # Post a message to the chat
        message_url = f'{self.base_url}/chat-completion/completions/simple'
        message_payload = {
            "chatId": chat_id,
            "prompt": prompt,
            "model": model,
            "bestOf": 0,
            "echo": True,
            "frequencyPenalty": 0,
            "logitBias": {},
            "logprobs": 0,
            "maxTokens": 0,
            "n": 0,
            "presencePenalty": 0,
            "seed": 0,
            "stop": True,
            "stream": True,
            "streamOptions": "string",
            "suffix": "string",
            "temperature": 0,
            "topP": 0,
            "user": "string",
            "expertIds": expert_ids,
            "collectionIds": collection_ids
        }
        try:
            headers = self.get_headers()
            headers["X-Persist-To-User-Store"] = str(store_in_db).lower()

            message_response = requests.post(message_url, json=message_payload, headers=headers)
            message_response.raise_for_status()  # Check for HTTP errors
        except requests.exceptions.RequestException as e:
            self.log(f"Failed to get response for prompt: {prompt}", logLevel=3)
            self.log(f"Error: {e}", logLevel=3)
            return "Unknown", chat_id
        response_dict = json.loads(message_response.text)
        bot_message = response_dict.get('botMessage')
        chat_message = bot_message.get('chatMessage')
        return chat_message, chat_id
    

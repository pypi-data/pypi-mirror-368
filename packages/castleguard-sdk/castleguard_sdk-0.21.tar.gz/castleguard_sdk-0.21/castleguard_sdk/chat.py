

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

    def chat_with_collection(self, prompt, collection_id=None, chat_id=None):
        """
        Interacts with the chat endpoint to generate a response from the model.

        :param prompt: The input prompt to send to the model.
        :param chat_id: Optional chat session ID.
        :return: Chatbot response or 'Unknown' if the request fails.
        """

        # create a new chat session
        if chat_id is None:
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

    def send_message_to_chat(self, chat_id, prompt, collection_ids=[], expert_ids=[], model="default", store_in_db=True, **kwargs):

        # Post a message to the chat
        message_url = f'{self.base_url}/chat-completion/completions/simple'
        message_payload = {
            "chatId": chat_id,
            "prompt": prompt,
            "model": model,
            "bestOf": 0 if "bestOf" not in kwargs else kwargs["bestOf"],
            "echo": True if "echo" not in kwargs else kwargs["echo"],
            "frequencyPenalty": 0 if "frequencyPenalty" not in kwargs else kwargs["frequencyPenalty"],
            "logitBias": {} if "logitBias" not in kwargs else kwargs["logitBias"],
            "logprobs": 0 if "logprobs" not in kwargs else kwargs["logprobs"],
            "maxTokens": 0 if "maxTokens" not in kwargs else kwargs["maxTokens"],
            "n": 0 if "n" not in kwargs else kwargs["n"],
            "presencePenalty": 0 if "presencePenalty" not in kwargs else kwargs["presencePenalty"],
            "seed": 0 if "seed" not in kwargs else kwargs["seed"],
            "stop": True if "stop" not in kwargs else kwargs["stop"],
            "stream": True if "stream" not in kwargs else kwargs["stream"],
            "streamOptions": "string" if "streamOptions" not in kwargs else kwargs["streamOptions"],
            "suffix": "string" if "suffix" not in kwargs else kwargs["suffix"],
            "temperature": 0 if "temperature" not in kwargs else kwargs["temperature"],
            "topP": 0 if "topP" not in kwargs else kwargs["topP"],
            "user": "string" if "user" not in kwargs else kwargs["user"],
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
    

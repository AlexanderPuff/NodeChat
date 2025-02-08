# NodeChat

A simple chat interface for your favorite OpenAI compatible LLM API, all within your terminal. I wrote and tested this for [DeepSeek-v3](https://www.deepseek.com) only, but most vendors should work out of the box or with minimal adjustments. My main goal and reason for writing this app was that most other light-weight chat interfaces do not support full conversation trees: Editing a previous message to start a new branch and later going back to the original is fully supported here.

## Controls

As the user interface consists of only the terminal, NodeChat is controlled with only a keyboard.

__Chat:__
- __ENTER__: Start typing a message, press Enter again to send.
- __Arrow keys__: Navigate the conversation tree. __UP__ to go to a previous message, __DOWN__ to go to a following message (if there are any), __LEFT__/__RIGHT__ to swap between different versions of the same message (for example after editing). Note: __RIGHT__ is also used to generate a new response if the last alternative is already selected, this will start a new branch.
- __e__: Edit the current message. __ENTER__ to save the edit, __ESC__ to cancel; If you edit one of your own messages a new reply will be generated automatically. Editing also starts a new branch.
- __s__: Open the settings screen, where you can adjust parameters such as temperature and change the API URL, key, and the model used.
- __c__: Start a new chat. You get the option to save the current chat.
- __q__: Quit; Here you can also save the current chat.

__Load Chats:__
- You can load a previous chat by selecting one from the table (with __UP__/__DOWN__) and confirming with __ENTER__. This will place you right where you saved last time.
- You can also start a new chat by pressing __n__ and then selecting a system prompt in the same way. Note: Place new prompts inside ```.\userInfo\prompts``` as ```.txt``` files alongside ```standardAssistant.txt```.

__Change Settings:__

Select the setting you want to change from the table and enter a new value, reset (and delete) config file with __r__, save and return to chat with __s__.

## Installation

This is pure python code, so simply cloning this repo and installing its dependencies via ```pip install -r requirements.txt``` is sufficient. When you launch this script for the first time (by calling ```main.py```), enter your API key (and change URL or model), and you are all set up!
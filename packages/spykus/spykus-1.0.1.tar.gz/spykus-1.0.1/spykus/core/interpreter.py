"""Interpreter for Script programming language."""

import random
import time
import sys
import os
import io
import tkinter as tk
import requests
import json
import threading
from typing import Dict, Any, Callable

root = None
widgets = []
entries = []

_original_stdout = sys.stdout
sys.stdout = io.StringIO()

import pygame

sys.stdout = _original_stdout
_interpreter_instance = None

pygame.mixer.init()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def builtin_play_music(args):
    file = args[0]
    wait = args[1] if len(args) > 1 else True  # по умолчанию ждать завершения

    path = resource_path(file)
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

    if wait:
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

def builtin_stop_music(args=None):
    pygame.mixer.music.stop()

# HTTP request functions
def builtin_http_get(args):
    """GET request. Args: [url, headers_dict (optional)]"""
    url = args[0]
    headers = args[1] if len(args) > 1 else {}
    
    try:
        response = requests.get(url, headers=headers)
        return {
            'status_code': response.status_code,
            'text': response.text,
            'headers': dict(response.headers),
            'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
        }
    except requests.RequestException as e:
        return {
            'error': str(e),
            'status_code': None,
            'text': None,
            'headers': {},
            'json': None
        }

def builtin_http_post(args):
    """POST request. Args: [url, data_dict (optional), headers_dict (optional)]"""
    url = args[0]
    data = args[1] if len(args) > 1 else {}
    headers = args[2] if len(args) > 2 else {}
    
    try:
        # Если data - это словарь, отправляем как JSON
        if isinstance(data, dict):
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
        
        return {
            'status_code': response.status_code,
            'text': response.text,
            'headers': dict(response.headers),
            'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
        }
    except requests.RequestException as e:
        return {
            'error': str(e),
            'status_code': None,
            'text': None,
            'headers': {},
            'json': None
        }

def builtin_http_put(args):
    """PUT request. Args: [url, data_dict (optional), headers_dict (optional)]"""
    url = args[0]
    data = args[1] if len(args) > 1 else {}
    headers = args[2] if len(args) > 2 else {}
    
    try:
        if isinstance(data, dict):
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, json=data, headers=headers)
        else:
            response = requests.put(url, data=data, headers=headers)
        
        return {
            'status_code': response.status_code,
            'text': response.text,
            'headers': dict(response.headers),
            'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
        }
    except requests.RequestException as e:
        return {
            'error': str(e),
            'status_code': None,
            'text': None,
            'headers': {},
            'json': None
        }

def builtin_http_delete(args):
    """DELETE request. Args: [url, headers_dict (optional)]"""
    url = args[0]
    headers = args[1] if len(args) > 1 else {}
    
    try:
        response = requests.delete(url, headers=headers)
        return {
            'status_code': response.status_code,
            'text': response.text,
            'headers': dict(response.headers),
            'json': response.json() if 'application/json' in response.headers.get('content-type', '') else None
        }
    except requests.RequestException as e:
        return {
            'error': str(e),
            'status_code': None,
            'text': None,
            'headers': {},
            'json': None
        }

def builtin_json_parse(args):
    """Parse JSON string. Args: [json_string]"""
    try:
        return json.loads(args[0])
    except json.JSONDecodeError as e:
        return {'error': str(e)}

def builtin_json_stringify(args):
    """Convert object to JSON string. Args: [object]"""
    try:
        return json.dumps(args[0], ensure_ascii=False)
    except TypeError as e:
        return f"Error: {str(e)}"

# Telebot functions
class TeleBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.handlers = {}
        self.running = False
        self.last_update_id = 0
        self.polling_thread = None
        
    def send_message(self, chat_id: int, text: str, parse_mode: str = None, reply_markup: dict = None):
        """Send message to chat"""
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
            
        response = requests.post(f"{self.base_url}/sendMessage", json=data)
        return response.json()
    
    def edit_message_text(self, chat_id: int, message_id: int, text: str, parse_mode: str = None, reply_markup: dict = None):
        """Edit message text"""
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
        if reply_markup:
            data['reply_markup'] = reply_markup
            
        response = requests.post(f"{self.base_url}/editMessageText", json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False):
        """Answer callback query"""
        data = {
            'callback_query_id': callback_query_id
        }
        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert
            
        response = requests.post(f"{self.base_url}/answerCallbackQuery", json=data)
        return response.json()
    
    def send_photo(self, chat_id: int, photo: str, caption: str = None, reply_markup: dict = None):
        """Send photo to chat"""
        data = {
            'chat_id': chat_id,
            'photo': photo
        }
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
            
        response = requests.post(f"{self.base_url}/sendPhoto", json=data)
        return response.json()
    
    def send_document(self, chat_id: int, document: str, caption: str = None, reply_markup: dict = None):
        """Send document to chat"""
        data = {
            'chat_id': chat_id,
            'document': document
        }
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
            
        response = requests.post(f"{self.base_url}/sendDocument", json=data)
        return response.json()
    
    def get_updates(self, offset: int = None, timeout: int = 30):
        """Get updates from Telegram"""
        params = {'timeout': timeout}
        if offset:
            params['offset'] = offset
            
        response = requests.get(f"{self.base_url}/getUpdates", params=params)
        return response.json()
    
    def get_me(self):
        """Get bot info"""
        response = requests.get(f"{self.base_url}/getMe")
        return response.json()
    
    def message_handler(self, commands=None, content_types=None):
        """Decorator for message handlers"""
        def decorator(func):
            handler_info = {
                'function': func,
                'commands': commands or [],
                'content_types': content_types or ['text']
            }
            if 'message' not in self.handlers:
                self.handlers['message'] = []
            self.handlers['message'].append(handler_info)
            return func
        return decorator
    
    def callback_query_handler(self, func=None):
        """Decorator for callback query handlers"""
        def decorator(func):
            handler_info = {
                'function': func
            }
            if 'callback_query' not in self.handlers:
                self.handlers['callback_query'] = []
            self.handlers['callback_query'].append(handler_info)
            return func
        return decorator if func is None else decorator(func)
    
    def process_update(self, update):
        """Process single update"""
        if 'message' in update:
            message = update['message']
            
            print(f"Processing message: {message.get('text', '')}")  # Debug
            
            # Process message handlers
            if 'message' in self.handlers:
                for handler in self.handlers['message']:
                    should_handle = False
                    
                    print(f"Checking handler with commands: {handler['commands']}")  # Debug
                    
                    # Check commands
                    if handler['commands']:
                        if 'text' in message and message['text'].startswith('/'):
                            command = message['text'].split()[0][1:]  # Remove '/'
                            print(f"Message command: {command}")  # Debug
                            if command in handler['commands']:
                                should_handle = True
                                print(f"Command match found: {command}")  # Debug
                    
                    # Check content types (if no commands specified)
                    elif not handler['commands']:
                        if 'text' in handler['content_types'] and 'text' in message:
                            should_handle = True
                        elif 'photo' in handler['content_types'] and 'photo' in message:
                            should_handle = True
                        elif 'document' in handler['content_types'] and 'document' in message:
                            should_handle = True
                    
                    if should_handle:
                        print(f"Calling handler function")  # Debug
                        try:
                            handler['function'](message)
                        except Exception as e:
                            print(f"Error in handler: {e}")
                            import traceback
                            traceback.print_exc()
        
        elif 'callback_query' in update:
            callback_query = update['callback_query']
            
            print(f"Processing callback query: {callback_query.get('data', '')}")  # Debug
            
            # Process callback query handlers
            if 'callback_query' in self.handlers:
                for handler in self.handlers['callback_query']:
                    try:
                        handler['function'](callback_query)
                    except Exception as e:
                        print(f"Error in callback handler: {e}")
                        import traceback
                        traceback.print_exc()
    
    def polling(self, none_stop=False):
        """Start polling for updates"""
        self.running = True
        
        print("Starting polling...")  # Debug
        
        def poll():
            while self.running:
                try:
                    updates = self.get_updates(offset=self.last_update_id + 1)
                    
                    if updates.get('ok') and updates.get('result'):
                        print(f"Received {len(updates['result'])} updates")  # Debug
                        for update in updates['result']:
                            self.process_update(update)
                            self.last_update_id = update['update_id']
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"Polling error: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(5)
        
        if none_stop:
            self.polling_thread = threading.Thread(target=poll, daemon=True)
            self.polling_thread.start()
        else:
            poll()
    
    def stop_polling(self):
        """Stop polling"""
        self.running = False
        if self.polling_thread:
            self.polling_thread.join()

# Global bot instance
_bot_instance = None

def builtin_bot_create(args):
    """Create telegram bot. Args: [token]"""
    global _bot_instance
    token = args[0]
    _bot_instance = TeleBot(token)
    return _bot_instance

def builtin_bot_send_message(args):
    """Send message. Args: [chat_id, text, parse_mode (optional), reply_markup (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    chat_id = args[0]
    text = args[1]
    parse_mode = args[2] if len(args) > 2 else None
    reply_markup = args[3] if len(args) > 3 else None
    
    return _bot_instance.send_message(chat_id, text, parse_mode, reply_markup)

def builtin_bot_edit_message_text(args):
    """Edit message text. Args: [chat_id, message_id, text, parse_mode (optional), reply_markup (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    chat_id = args[0]
    message_id = args[1]
    text = args[2]
    parse_mode = args[3] if len(args) > 3 else None
    reply_markup = args[4] if len(args) > 4 else None
    
    return _bot_instance.edit_message_text(chat_id, message_id, text, parse_mode, reply_markup)

def builtin_bot_answer_callback_query(args):
    """Answer callback query. Args: [callback_query_id, text (optional), show_alert (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    callback_query_id = args[0]
    text = args[1] if len(args) > 1 else None
    show_alert = args[2] if len(args) > 2 else False
    
    return _bot_instance.answer_callback_query(callback_query_id, text, show_alert)

def builtin_bot_send_photo(args):
    """Send photo. Args: [chat_id, photo_url, caption (optional), reply_markup (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    chat_id = args[0]
    photo_url = args[1]
    caption = args[2] if len(args) > 2 else None
    reply_markup = args[3] if len(args) > 3 else None
    
    return _bot_instance.send_photo(chat_id, photo_url, caption, reply_markup)

def builtin_bot_send_document(args):
    """Send document. Args: [chat_id, document_url, caption (optional), reply_markup (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    chat_id = args[0]
    document_url = args[1]
    caption = args[2] if len(args) > 2 else None
    reply_markup = args[3] if len(args) > 3 else None
    
    return _bot_instance.send_document(chat_id, document_url, caption, reply_markup)

def builtin_bot_get_me(args):
    """Get bot info. Args: []"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    return _bot_instance.get_me()

def builtin_bot_get_updates(args):
    """Get updates. Args: [offset (optional), timeout (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    offset = args[0] if len(args) > 0 else None
    timeout = args[1] if len(args) > 1 else 30
    
    return _bot_instance.get_updates(offset, timeout)

def builtin_bot_start_polling(args):
    """Start polling. Args: [none_stop (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    none_stop = args[0] if len(args) > 0 else False
    _bot_instance.polling(none_stop)

def builtin_bot_stop_polling(args):
    """Stop polling. Args: []"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    _bot_instance.stop_polling()

def builtin_bot_add_message_handler(args):
    """Add message handler. Args: [handler_function, commands (optional), content_types (optional)]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    handler_func = args[0]
    commands = args[1] if len(args) > 1 else None
    content_types = args[2] if len(args) > 2 else ['text']
    
    # Convert commands to list if it's a string
    if isinstance(commands, str):
        commands = [commands]
    
    print(f"Adding handler for commands: {commands}")  # Debug
    
    # Create a wrapper function that can evaluate the XoFunction
    def wrapper(message):
        global _interpreter_instance
        if _interpreter_instance is None:
            print("Error: No interpreter instance available")
            return

        print(f"Handler called with message: {message.get('text', '')}")  # Debug

        try:
            chat = message.get("chat")
            if isinstance(chat, dict):
                print(f"chat_id = {chat.get('id')}")
            from core.ast import XoCall, XoLiteral  # ИМПОРТ ВНУТРИ ФУНКЦИИ

            if isinstance(handler_func, str):
                func_name = handler_func
            else:
                func_name = handler_func.name if hasattr(handler_func, 'name') else str(handler_func)

            if func_name in _interpreter_instance.env:
                call_node = XoCall(func_name, [XoLiteral(message)])
                _interpreter_instance.eval(call_node)
            else:
                print(f"Handler function '{func_name}' not found in environment")

        except Exception as e:
            print(f"Error in handler: {e}")
            import traceback
            traceback.print_exc()

    
    # Add handler to bot
    handler_info = {
        'function': wrapper,
        'commands': commands or [],
        'content_types': content_types
    }
    
    if 'message' not in _bot_instance.handlers:
        _bot_instance.handlers['message'] = []
    
    print(f"Handler added successfully. Total handlers: {len(_bot_instance.handlers['message'])}")  # Debug
    
    # Add handler to bot
    handler_info = {
        'function': wrapper,  # Use the wrapper instead of the XoFunction directly
        'commands': commands or [],
        'content_types': content_types
    }
    
    if 'message' not in _bot_instance.handlers:
        _bot_instance.handlers['message'] = []
    _bot_instance.handlers['message'].append(handler_info)

def builtin_bot_add_callback_query_handler(args):
    """Add callback query handler. Args: [handler_function]"""
    if not _bot_instance:
        return {'error': 'Bot not created'}
    
    handler_func = args[0]
    
    print(f"Adding callback query handler")  # Debug
    
    # Create a wrapper function that can evaluate the XoFunction
    def wrapper(callback_query):
        global _interpreter_instance
        if _interpreter_instance is None:
            print("Error: No interpreter instance available")
            return

        print(f"Callback query handler called with data: {callback_query.get('data', '')}")  # Debug

        try:
            from core.ast import XoCall, XoLiteral  # ИМПОРТ ВНУТРИ ФУНКЦИИ

            if isinstance(handler_func, str):
                func_name = handler_func
            else:
                func_name = handler_func.name if hasattr(handler_func, 'name') else str(handler_func)

            if func_name in _interpreter_instance.env:
                call_node = XoCall(func_name, [XoLiteral(callback_query)])
                _interpreter_instance.eval(call_node)
            else:
                print(f"Callback handler function '{func_name}' not found in environment")

        except Exception as e:
            print(f"Error in callback handler: {e}")
            import traceback
            traceback.print_exc()

    
    # Add handler to bot
    handler_info = {
        'function': wrapper
    }
    
    if 'callback_query' not in _bot_instance.handlers:
        _bot_instance.handlers['callback_query'] = []
    _bot_instance.handlers['callback_query'].append(handler_info)
    
    print(f"Callback query handler added successfully. Total handlers: {len(_bot_instance.handlers['callback_query'])}")  # Debug

def builtin_create_inline_keyboard(args):
    buttons_matrix = args[0]
    
    return {
        "inline_keyboard": buttons_matrix
    }

def builtin_create_reply_keyboard(args):
    buttons_matrix = args[0]
    resize_keyboard = args[1] if len(args) > 1 else True
    one_time_keyboard = args[2] if len(args) > 2 else False
    
    # Convert strings to button objects
    keyboard = []
    for row in buttons_matrix:
        button_row = []
        for button in row:
            if isinstance(button, str):
                button_row.append({"text": button})
            else:
                button_row.append(button)
        keyboard.append(button_row)
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": resize_keyboard,
        "one_time_keyboard": one_time_keyboard
    }

def builtin_remove_keyboard(args):
    """Remove keyboard. Args: []"""
    return {
        "remove_keyboard": True
    }

def make_gui_env(env_ref):
    root = None
    widgets = []
    entries = []

    def builtin_window(args):
        nonlocal root, widgets, entries
        root = tk.Tk()
        root.title(args[0])
        root.geometry(f"{args[1]}x{args[2]}")
        widgets.clear()
        entries.clear()

    def builtin_add_label(args):
        lbl = tk.Label(root, text=args[0], font=("Segoe UI", 12))
        lbl.pack(pady=4)
        widgets.append(lbl)

    def builtin_add_button(args):
        text = args[0]
        call_node = args[1]

        def on_click():
            interpreter.eval(call_node)

        btn = tk.Button(root, text=text, command=on_click, font=("Segoe UI", 11))
        btn.pack(pady=6)

    def builtin_add_entry(args):
        entry = tk.Entry(root, font=("Segoe UI", 11))
        entry.pack(pady=4)
        entries.append(entry)
        widgets.append(entry)

    def builtin_get_entry(args):
        return entries[0].get() if entries else ""

    def builtin_run_window(args):
        root.mainloop()

    return {
        'window': builtin_window,
        'add_label': builtin_add_label,
        'add_button': builtin_add_button,
        'add_entry': builtin_add_entry,
        'get_entry': builtin_get_entry,
        'run_window': builtin_run_window
    }

class Interpreter:
    def __init__(self, env=None):
        global _interpreter_instance
        _interpreter_instance = self  # Store global reference
        
        self.env = {
            'len': lambda args: len(args[0]),
            'range': lambda args: list(range(args[0], args[1])) if len(args) == 2 else list(range(args[0])),
            'str': lambda args: str(args[0]),
            'round': lambda args: round(args[0]),
            'int': lambda args: int(args[0]),
            'float': lambda args: float(args[0]),
            'random': lambda args: random.random(),
            'randint': lambda args: random.randint(args[0], args[1]),
            'time': lambda args: time.time(),
            'exit': lambda args: exit(0),
            'play_music': builtin_play_music,
            'stop_music': builtin_stop_music,
            # HTTP request functions
            'http_get': builtin_http_get,
            'http_post': builtin_http_post,
            'http_put': builtin_http_put,
            'http_delete': builtin_http_delete,
            # JSON functions
            'json_parse': builtin_json_parse,
            'json_stringify': builtin_json_stringify,
            # Telegram Bot functions
            'bot_create': builtin_bot_create,
            'bot_send_message': builtin_bot_send_message,
            'bot_edit_message_text': builtin_bot_edit_message_text,
            'bot_answer_callback_query': builtin_bot_answer_callback_query,
            'bot_send_photo': builtin_bot_send_photo,
            'bot_send_document': builtin_bot_send_document,
            'bot_get_me': builtin_bot_get_me,
            'bot_get_updates': builtin_bot_get_updates,
            'bot_start_polling': builtin_bot_start_polling,
            'bot_stop_polling': builtin_bot_stop_polling,
            'bot_add_message_handler': builtin_bot_add_message_handler,
            'bot_add_callback_query_handler': builtin_bot_add_callback_query_handler,
            # Keyboard functions
            'create_inline_keyboard': builtin_create_inline_keyboard,
            'create_reply_keyboard': builtin_create_reply_keyboard,
            'remove_keyboard': builtin_remove_keyboard,
        }

        # Добавляем GUI-функции с замыканием на self.env
        self.env.update(make_gui_env(self.env))

        if env:
            self.env.update(env)

    def eval(self, node):
        if func := getattr(node, '_eval', None):
            return func(self, node)
        raise TypeError(f"Unknown node type: {type(node).__name__}")
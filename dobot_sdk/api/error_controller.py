# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
Error code handling module
Provides functionality to retrieve robot alarm information via HTTP interface
"""

import requests
import json
from typing import List, Dict, Optional, Any

# Supported languages list
SUPPORTED_LANGUAGES = [
    ("中文", "zh_cn"),
    ("English", "en"),
    ("日本语", "ja"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Русский", "ru"),
    ("韩国语", "ko"),
    ("繁体中文", "zh_hant"),
    ("越南语", "vi"),
    ("法语", "fr")
]


class ErrorController:
    """
    Error controller class

    Retrieve robot alarm information via HTTP interface
    Example:
        error_ctrl = ErrorController("192.168.1.100")
        error_info = error_ctrl.GetError("zh_cn")
        formatted_error = error_ctrl.GetErrorFormatted("zh_cn")
    """
    
    def __init__(self, ip: str):
        """
        Initialize error controller

        Args:
            ip: Robot IP address
        """
        self.ip = ip
    
    def SetLanguage(self, language: str = "zh_cn") -> bool:
        """
        Set robot language

        Args:
            language: Language code, supported languages
                     "zh_cn" - Simplified Chinese
                     "zh_hant" - Traditional Chinese
                     "en" - English
                     "ja" - Japanese
                     "de" - German
                     "vi" - Vietnamese
                     "es" - Spanish
                     "fr" - French
                     "ko" - Korean
                     "ru" - Russian

        Returns:
            Whether the setting was successful
        """
        try:
            language_url = f"http://{self.ip}:22000/interface/language"
            language_data = {"type": language}
            
            response = requests.post(language_url, json=language_data, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Failed to set language: {e}")
            return False
    
    def GetError(self, language: str = "zh_cn") -> Dict[str, Any]:
        """
        Get robot alarm information

        Args:
            language: Language setting, defaults to "zh_cn"

        Returns:
            dict: Alarm information dictionary, format as follows:
            {
                "errMsg": [
                    {
                        "id": xxx,
                        "level": xxx,
                        "description": "xxx",
                        "solution": "xxx",
                        "mode": "xxx",
                        "date": "xxxx",
                        "time": "xxxx"
                    }
                ]
            }
            If no alarms, returns {"errMsg": []}
        """
        try:
            # First set the language
            self.SetLanguage(language)
            
            # Get alarm information
            alarm_url = f"http://{self.ip}:22000/protocol/getAlarm"
            response = requests.get(alarm_url, timeout=5)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # If empty object returned, convert to standard format
                    if result == {} or result is None:
                        return {"errMsg": []}
                    return result
                except json.JSONDecodeError:
                    # If empty response or non-JSON format, treat as no alarms
                    return {"errMsg": []}
            else:
                print(f"Failed to get alarm information: HTTP {response.status_code}")
                return {"errMsg": []}
                
        except requests.exceptions.RequestException as e:
            print(f"HTTP request exception: {e}")
            return {"errMsg": []}
        except Exception as e:
            print(f"Unknown error occurred while getting alarm information: {e}")
            return {"errMsg": []}
    
    def GetErrorFormatted(self, language: str = "zh_cn") -> str:
        """
        Get formatted robot alarm information

        Args:
            language: Language setting

        Returns:
            str: Formatted alarm information string
        """
        error_info = self.GetError(language)
        return self._format_error_messages(error_info)
    
    def _format_error_messages(self, error_info: Dict[str, Any]) -> str:
        """
        Format error information

        Args:
            error_info: Alarm information returned by get_error()

        Returns:
            str: Formatted error information string
        """
        err_msg_list = error_info.get("errMsg", [])
        
        if not err_msg_list:
            return "No alarm information"
        
        messages = []
        for err in err_msg_list:
            error_id = err.get("id", "Unknown")
            level = err.get("level", "")
            description = err.get("description", "")
            solution = err.get("solution", "")
            mode = err.get("mode", "")
            date = err.get("date", "")
            time = err.get("time", "")
            
            msg = f"Error code {error_id}"
            if level:
                msg += f"\nLevel: {level}"
            if description:
                msg += f"\nDescription: {description}"
            if solution:
                msg += f"\nSolution: {solution}"
            if mode:
                msg += f"\nMode: {mode}"
            if date and time:
                msg += f"\nTime: {date} {time}"
            
            messages.append(msg)
        
        return "\n\n".join(messages)
    
    # Backward compatibility aliases (snake_case -> PascalCase)
    set_language = SetLanguage
    get_error = GetError
    get_error_formatted = GetErrorFormatted


def parse_error_ids(error_response: Optional[str]) -> List[int]:
    """
    Parse error code response string (for TCP interface GetErrorID command)

    Args:
        error_response: Error code response from robot, format is "0,{[1537,2048,2049]},GetErrorID();"

    Returns:
        Parsed list of error codes
    """
    if not error_response:
        return []
    
    # If it's an error message rather than error code response, return empty list
    if isinstance(error_response, str):
        # Check if it's an error message (e.g., "Control Mode Is Not Tcp")
        if not error_response.strip().startswith('0,'):
            print(f"Received error message instead of error code: {error_response}")
            return []
    
    try:
        # Remove trailing ";GetErrorID()"
        if error_response.endswith('GetErrorID();'):
            error_response = error_response[:-len('GetErrorID();')].strip()
        
        # Format is ,{[1537,2048,2049]}
        # Extract the list part inside braces        start = error_response.find('{[')
        end = error_response.find(']}')
        
        if start != -1 and end != -1:
            list_str = error_response[start+2:end]
            error_ids = [int(x.strip()) for x in list_str.split(',') if x.strip()]
            return error_ids
        else:
            # Try to parse directly as integer
            return [int(error_response.strip())]
    except ValueError as e:
        # Parsing failed, return empty list
        print(f"Failed to parse error code: {e}")
        return []
    except Exception as e:
        print(f"Failed to parse error code: {e}")
        return []


# Keep original standalone function interfaces for backward compatibility
def set_language(ip: str, language: str = "zh_cn") -> bool:
    """
    Set robot language (legacy interface compatible)

    Args:
        ip: Robot IP address
        language: Language code

    Returns:
        Whether the setting was successful
    """
    return ErrorController(ip).SetLanguage(language)


def get_error(ip: str, language: str = "zh_cn") -> Dict[str, Any]:
    """
    Get robot alarm information (legacy interface compatible)

    Args:
        ip: Robot IP address
        language: Language setting

    Returns:
        Alarm information dictionary
    """
    return ErrorController(ip).GetError(language)


def format_error_messages_from_http(error_info: Dict[str, Any]) -> str:
    """
    Format error information from HTTP interface (legacy interface compatible)

    Args:
        error_info: Alarm information returned by get_error()

    Returns:
        Formatted error information string
    """
    err_msg_list = error_info.get("errMsg", [])
    
    if not err_msg_list:
        return "No alarm information"
    
    messages = []
    for err in err_msg_list:
        error_id = err.get("id", "Unknown")
        level = err.get("level", "")
        description = err.get("description", "")
        solution = err.get("solution", "")
        mode = err.get("mode", "")
        date = err.get("date", "")
        time = err.get("time", "")
        
        msg = f"Error code {error_id}"
        if level:
            msg += f"\nLevel: {level}"
        if description:
            msg += f"\nDescription: {description}"
        if solution:
            msg += f"\nSolution: {solution}"
        if mode:
            msg += f"\nMode: {mode}"
        if date and time:
            msg += f"\nTime: {date} {time}"
        
        messages.append(msg)
    
    return "\n\n".join(messages)
from langchain_core.tools import tool
from datetime import date as _date

@tool
def ask_user(input_prompt: str) -> str:
    """Ask the user to enter what they'd like to do this. The message will be displayed as a prompt. Always use this if we need input or direction from the user."""
    user_input = input(f"💬 {input_prompt}\n👉 Enter Message: ")
    return user_input

@tool
def search_event(date: _date, user_input: str):
    """Use this once you have all information about the users"""
    pass
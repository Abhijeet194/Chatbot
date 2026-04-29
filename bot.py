import os
import re
import time
import pyautogui
import pyperclip
from openai import OpenAI


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


last_processed_message = None

MY_NAMES = {"abhijeet", "abhijeet kumar"}


def get_last_message_info(chat_history: str):
    lines = [line.strip() for line in chat_history.strip().splitlines() if line.strip()]
    if not lines:
        return None, None

    last_line = lines[-1]
    print("DEBUG last_line:", last_line)

 
    match = re.search(r"\]\s*(.*?):\s*(.*)", last_line)
    if match:
        sender = match.group(1).strip()
        message = match.group(2).strip()
        return sender, message

   
    return None, last_line


def should_reply(chat_history: str) -> bool:
    global last_processed_message

    sender, message = get_last_message_info(chat_history)

    if not message:
        print("No message detected")
        return False

    print("Last message:", message)

    if message == last_processed_message:
        print("Duplicate message detected")
        return False

    if sender:
        print("Detected sender:", sender)
        if sender.lower() in MY_NAMES:
            return False
    else:
        print("No sender detected -> fallback mode")

    last_processed_message = message
    return True


def get_chat_history():
    pyautogui.moveTo(501, 397)
    pyautogui.dragTo(1016, 655, duration=1.0, button="left")
    time.sleep(1)

    pyautogui.hotkey("ctrl", "c")
    pyautogui.click(825, 644)
    time.sleep(1)

    return pyperclip.paste()


def type_and_send_reply(text: str):
    pyperclip.copy(text)


    pyautogui.click(875, 689)
    time.sleep(0.5)

    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)
    pyautogui.press("enter")


def generate_reply(chat_history: str) -> str:
    completion = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Abhijeet. You speak Hindi and English. "
                    "Reply naturally, briefly, and like a human. "
                    "No emojis. No extra explanation."
                ),
            },
            {"role": "user", "content": chat_history},
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content.strip()


def main():
   
    pyautogui.click(606, 743)
    time.sleep(2)

    while True:
        try:
            chat_history = get_chat_history()

            if not chat_history.strip():
                print("Clipboard empty, retrying...")
                time.sleep(3)
                continue

            print("\n--- CHAT HISTORY ---")
            print(chat_history)

            if not should_reply(chat_history):
                print("Waiting for new message...\n")
                time.sleep(5)
                continue

            response = generate_reply(chat_history)
            print("AI Response:", response)

            if response:
                type_and_send_reply(response)
                print("Reply sent.\n")
            else:
                print("Empty response, not sending.\n")

            time.sleep(8)

        except Exception as e:
            print("ERROR:", repr(e))
            time.sleep(5)


if __name__ == "__main__":
    main()
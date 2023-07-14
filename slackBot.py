import os
from pathlib import Path
import re
from dotenv import load_dotenv
from slack_sdk import WebClient
from emailIntegration import scrape_email
from slackeventsapi import SlackEventAdapter
from flask import Flask


app = Flask(__name__)

def main():
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # Create a Slack client
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    email_content_lines = scrape_email()
    if email_content_lines:
        # Initialize counter for the news
        news_counter = 1

        # Prepare final content
        final_content = ''

        # Go through each line of the email content
        for line in range(len(email_content_lines)):
            # Check if the line is a title (it's in uppercase)
            if email_content_lines[line][:5].isupper():
                # Make the title bold and add a news counter in front of it
                if email_content_lines[line-1].isupper():
                    final_content += f"*{email_content_lines[line][:-1]}*\n"
                else:
                    final_content += f"{news_counter}. *{email_content_lines[line][:-1]}*\n"
                    news_counter += 1
            else:
                # Just add the line to the final content
                final_content += f"{email_content_lines[line]}\n"


        response = client.chat_postMessage(channel='#bot2', text="*Whats happening with AI around the world*\n" + final_content.strip())
        if response['ok']:
            print("Message sent successfully!")
        else:
            print("Failed to send message:", response['error'])
    
    else:
        print("No data to print")

if __name__ == '__main__':
    main()

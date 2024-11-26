import json

import click
from openai import OpenAI


class MessageGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_message(self, diff: str, original_message: str) -> str:
        """Generate an improved commit message based on the diff."""
        try:
            prompt = f"""Analyze the git diff and original commit message below, then generate a clear, concise, and descriptive commit message.
            The message should be brief but informative (ideally under 72 characters).
            Return the response in JSON format with a 'message' field containing the commit message.
            
            Original message: {original_message}
            
            Diff:
            {diff}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates clear, concise git commit messages. Always respond with valid JSON containing a 'message' field. Keep messages brief but informative."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response and extract the message
            message_json = json.loads(response.choices[0].message.content)
            return message_json['message'].strip()
        except Exception as e:
            raise click.ClickException(f"Failed to generate message: {str(e)}")
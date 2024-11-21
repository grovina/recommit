import click
from openai import OpenAI


class MessageGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_message(self, diff: str, original_message: str) -> str:
        """Generate an improved commit message based on the diff."""
        try:
            prompt = f"""Given the following git diff and original commit message,
            generate a clear and descriptive commit message that explains the changes:
            
            Original message: {original_message}
            
            Diff:
            {diff}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates clear git commit messages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Add some creativity but keep it focused
                max_tokens=200    # Reasonable length for commit messages
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise click.ClickException(f"Failed to generate message: {str(e)}")
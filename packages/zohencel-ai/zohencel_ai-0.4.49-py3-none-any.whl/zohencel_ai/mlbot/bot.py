import subprocess
import webbrowser
import time,os

class ZohencelmlBot:
    """
    A class to manage the Zohencelml bot and provide the Groq API key.
    """

    DEFAULT_GROQ_API_KEY = "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"  # Default API key
    DEFAULT_GROQ_MODEL = "llama3-70b-8192"
    def __init__(self, groq_api_key: str = None,groq_model: str = None):
        """
        Initializes the bot with the Groq API key. If not provided, uses the default API key.
        
        Parameters:
            groq_api_key (str, optional): The Groq API key (default is provided).
        """
        self.groq_api_key = groq_api_key or self.DEFAULT_GROQ_API_KEY
        self.groq_model = groq_model or self.DEFAULT_GROQ_MODEL
    def get_groq_api_key(self) -> str:
        """
        Returns the Groq API key.

        Returns:
            str: The Groq API key.
        """
        return self.groq_api_key
    def get_groq_model(self) -> str:
        return self.groq_model
    def run(self):
        """
        Launches the FastAPI app using `uvicorn main:app` command and opens the browser.
        """
        try:
            print("Launching FastAPI app using uvicorn...")
            
            # Start the FastAPI app in a subprocess
            process = subprocess.Popen(
                ["uvicorn", "zohencel_ai.mlbot.main:app"], cwd=os.path.dirname(__file__)
            )
            
            # Wait for a moment to allow the server to start
            time.sleep(3)
            
            # Open the browser with the specified URL
            url = "https://zohencelai.github.io/MLBot/"
            print(f"Opening browser at {url}...")
            webbrowser.open(url)
            
            # Wait for the subprocess to complete (if needed)
            process.wait()
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch FastAPI app: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

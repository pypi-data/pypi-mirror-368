import subprocess
import os


class Analysischartbot:
    """
    A class to launch a specific Streamlit app programmatically and manage the Groq API key.
    """

    APP_FILENAME = "chart_bot.py"  # Hardcoded Streamlit app filename

    def __init__(self, groq_api_key: str = "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"):
        """
        Initializes the launcher with the Streamlit app path and optional Groq API key.
        
        Parameters:
            groq_api_key (str): The Groq API key (default is provided).
        """
        self.app_path = os.path.join(os.path.dirname(__file__), self.APP_FILENAME)
        self.groq_api_key = groq_api_key

    def _validate_app_file(self):
        """
        Validates if the Streamlit app file exists.

        Raises:
            FileNotFoundError: If the specified app file does not exist.
        """
        if not os.path.isfile(self.app_path):
            raise FileNotFoundError(f"Streamlit app file not found at: {self.app_path}")

    def run(self):
        """
        Launches the Streamlit app using `streamlit run` command.
        """
        self._validate_app_file()
        try:
            print(f"Launching Streamlit app: {self.app_path}")
            subprocess.run(["streamlit", "run", self.app_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch Streamlit app: {e}")

    def get_groq_api_key(self) -> str:
        """
        Returns the Groq API key.

        Returns:
            str: The stored Groq API key.
        """
        return self.groq_api_key


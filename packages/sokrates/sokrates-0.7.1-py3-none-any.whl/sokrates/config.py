# This script defines the `Config` class, which is responsible for managing
# application-wide configuration settings. It loads environment variables
# from a `.env` file, providing default values for API endpoints, API keys,
# and the default LLM model. This centralizes configuration management
# and allows for easy customization via environment variables.

import os
from pathlib import Path
from dotenv import load_dotenv
from .colors import Colors
from datetime import datetime

class Config:
  """
  Manages configuration settings for the LLM tools application.
  Loads environment variables from a .env file and provides default values
  for various settings like API endpoint, API key, and default model.
  """
  
  DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
  DEFAULT_API_KEY = "notrequired"
  DEFAULT_MODEL = "qwen/qwen3-8b"
  DEFAULT_MODEL_TEMPERATURE = 0.7
  DEFAULT_PROMPTS_DIRECTORY = Path(f"{Path(__file__).parent.resolve()}/prompts").resolve()
  DEFAULT_TASK_QUEUE_DAEMON_PROCESSING_INTERVAL = 15
  
  _instance = None  # Class variable to hold the single instance

  def __new__(cls, *args, **kwargs):
        """
        Singleton pattern implementation to ensure only one instance of Config exists.
        
        Returns:
            Config: The single instance of the Config class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
  
  def __init__(self, verbose=False) -> None:
    """
    Initializes the Config object.

    Args:
        verbose (bool): If True, prints basic configuration details upon loading.
    """
    if not hasattr(self, 'initialized'):
      self.initialized = True
      self.verbose = verbose
      # Determine the configuration file path. Prioritize SOKRATES_CONFIG_FILEPATH environment variable.
      self.home_path: str = f"{str(Path.home())}/.sokrates"
      self.config_path: str = f"{self.home_path}/.env"
      self.logs_path: str = f"{self.home_path}/logs"
      self.daemon_logfile_path: str = f"{self.logs_path}/daemon.log"
      self.task_queue_daemon_processing_interval = self.DEFAULT_TASK_QUEUE_DAEMON_PROCESSING_INTERVAL
      self.database_path: str = f"{self.home_path}/sokrates_database.sqlite"
      self.config_path: str = os.environ.get('SOKRATES_CONFIG_FILEPATH', self.config_path)
      if os.environ.get('SOKRATES_DATABASE_PATH'):
        self.database_path: str = os.environ.get('SOKRATES_DATABASE_PATH')
      if os.environ.get('SOKRATES_TASK_QUEUE_DAEMON_LOGFILE_PATH'):
        self.daemon_logfile_path: str = os.environ.get('SOKRATES_TASK_QUEUE_DAEMON_LOGFILE_PATH')      
      self.load_env()
      self.initialize_directories()
      self.print_configuration()
    
  def print_configuration(self):
      """
      Prints the current configuration settings to the console in a formatted way.
      
      This method displays various configuration parameters such as:
      - SOKRATES_HOME_PATH
      - SOKRATES_API_ENDPOINT  
      - SOKRATES_DEFAULT_MODEL
      - SOKRATES_DEFAULT_MODEL_TEMPERATURE
      - SOKRATES_CONFIG_FILEPATH
      - SOKRATES_DATABASE_PATH
      - SOKRATES_DAEMON_LOGFILE_PATH
      
      Returns:
          None
      """
      if self.verbose:
        print(f"{Colors.GREEN}{Colors.BOLD}### Basic Configuration ###{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_HOME_PATH: {self.home_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_API_ENDPOINT: {self.api_endpoint}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DEFAULT_MODEL: {self.default_model}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DEFAULT_MODEL_TEMPERATURE: {self.default_model_temperature}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_CONFIG_FILEPATH: {self.config_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DATABASE_PATH: {self.database_path}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD} - SOKRATES_DAEMON_LOGFILE_PATH: {self.daemon_logfile_path}{Colors.RESET}")
  
  def load_env(self) -> None:
      """
      Loads environment variables from the specified .env file.
      Sets API endpoint, API key, and default model, applying defaults if not found.
      """
      load_dotenv(self.config_path)
      self.api_endpoint: str | None = os.environ.get('SOKRATES_API_ENDPOINT', self.DEFAULT_API_ENDPOINT)
      self.api_key: str | None = os.environ.get('SOKRATES_API_KEY', self.DEFAULT_API_KEY)
      self.default_model: str | None = os.environ.get('SOKRATES_DEFAULT_MODEL', self.DEFAULT_MODEL)
      self.default_model_temperature: float | None = float(os.environ.get('SOKRATES_DEFAULT_MODEL_TEMPERATURE', self.DEFAULT_MODEL_TEMPERATURE))
      
  def initialize_directories(self):
    """
    Creates the necessary directory structure for the application.
    
    This method ensures that the following directories exist:
    - The main sokrates home directory (~/.sokrates)
    - The logs subdirectory (~/.sokrates/logs)
    
    Returns:
        None
    """
    if self.verbose:
      print(f"Creating sokrates home path: {self.home_path}")
    
    Path(self.home_path).mkdir(parents=True, exist_ok=True)
    
    if self.verbose:
      print(f"Creating sokrates logs path: {self.logs_path}")
    
    Path(self.logs_path).mkdir(parents=True, exist_ok=True)
  
  @staticmethod
  def _get_local_member_value(key):
    """
    Retrieves the value of a local member variable by key.

    This static method is used internally to fetch configuration values
    from the singleton instance of Config. It checks for specific keys and returns
    their corresponding values or None if not found.

    Args:
        key (str): The configuration parameter name to retrieve.
            Valid keys include: 'api_endpoint', 'api_key', 'default_model',
            'default_model_temperature', 'database_path', and 'task_queue_daemon_logfile_path'.

    Returns:
        The value of the requested configuration parameter, or None if not found.
    """
    if key == 'api_endpoint':
      return Config._instance.api_endpoint 
    if key == 'api_key':
      return Config._instance.api_endpoint 
    if key == 'default_model':
      return Config._instance.default_model
    if key == 'default_model_temperature':
      return Config._instance.default_model_temperature
    if key == 'database_path':
      return Config._instance.database_path
    if key == 'task_queue_daemon_logfile_path':
      return Config._instance.daemon_logfile_path
    return None
  
  @staticmethod
  def get(key, default_value=None):
    """
    Retrieves a configuration value by key.

    This method first checks if the requested key exists in the local Config instance,
    and returns its value if found. If not found locally, it falls back to checking
    the environment variables for a matching key.

    Args:
        key (str): The configuration parameter name to retrieve.
        default_value (any, optional): A default value to return if the key is not found.

    Returns:
        The configuration value for the specified key, or the default_value if not found.
    """
    lval = Config._get_local_member_value(key)
    if lval:
      return lval
    return os.environ.get(key, default_value)
  
  @staticmethod
  def create_and_return_task_execution_directory(output_directory=None):
    """
    Creates and returns the target directory for task results.

    Args:
        output_directory (Path, optional): Path to custom output directory.
            If provided, creates this directory. If None, uses default path in $HOME/.sokrates/tasks/results/YYYY-MM-DD_HH-mm .

    Returns:
        Path: Path object pointing to the created directory

    Raises:
        FileExistsError: If the specified output directory already exists
    """
    if output_directory:
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        return output_directory
    
    # use default if not specified
    now = datetime.now()
    home_dir = Path.home()
    
    # Format the directory name as 'YYYY-MM-DD_HH-MM'
    directory_name = now.strftime("%Y-%m-%d_%H-%M")
    
    default_task_result_parent_dir = home_dir / ".sokrates" / "tasks" / "results"
    target_dir = Path(default_task_result_parent_dir) / directory_name
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    
    return target_dir

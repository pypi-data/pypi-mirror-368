import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .client import PromptlyzerClient

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages prompts with automatic updates from the Promptlyzer API.
    Fetches the latest versions of prompts and caches them locally.
    """
    
    def __init__(
        self,
        client: PromptlyzerClient,
        project_id: str,
        update_interval: int = 180,
        on_update_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        """
        Initialize a new PromptManager.
        
        Args:
            client: The PromptlyzerClient to use for API requests.
            project_id: The ID of the project to fetch prompts from.
            update_interval: How often to check for updates in seconds (default: 180).
            on_update_callback: Optional callback function that is called when a prompt is updated.
                                The callback receives the prompt name and the updated prompt data.
        """
        self.client = client
        self.project_id = project_id
        self.update_interval = update_interval
        self.on_update_callback = on_update_callback
        
        self._prompts: Dict[str, Dict[str, Any]] = {}
        
        self._last_versions: Dict[str, int] = {}
        
        self._lock = threading.RLock()
        
        self._stop_updates = False
        
        # Background thread for updates
        self._update_thread = None
    
    def start(self):
        """Start the automatic update process in the background."""
        if self._update_thread is not None:
            logger.warning("Update process is already running")
            return
        
        self._fetch_all_prompts()
        
        # Start the background thread
        self._stop_updates = False
        self._update_thread = threading.Thread(
            target=self._update_loop,
            daemon=True
        )
        self._update_thread.start()
        logger.info(f"Started prompt update thread for project {self.project_id}")
    
    def stop(self):
        """Stop the automatic update process."""
        if self._update_thread is None:
            logger.warning("Update process is not running")
            return
        
        self._stop_updates = True
        self._update_thread.join(timeout=10)  # Wait for the thread to finish
        self._update_thread = None
        logger.info(f"Stopped prompt update thread for project {self.project_id}")
    
    def get_prompt(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a prompt by name from the local cache.
        
        Args:
            prompt_name: The name of the prompt.
            
        Returns:
            Dict[str, Any] or None: The prompt data if found, otherwise None.
        """
        with self._lock:
            return self._prompts.get(prompt_name)
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all prompts from the local cache.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping prompt names to their data.
        """
        with self._lock:
            return self._prompts.copy()
    
    def refresh(self) -> Dict[str, Dict[str, Any]]:
        """
        Force an immediate refresh of all prompts.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping prompt names to their data.
        """
        self._fetch_all_prompts()
        return self.get_all_prompts()
    
    def _update_loop(self):
        """Background thread loop that periodically checks for updates."""
        while not self._stop_updates:
            # Sleep first to avoid immediate double-fetch after the initial load in start()
            for _ in range(self.update_interval):
                if self._stop_updates:
                    return
                time.sleep(1)
            
            try:
                self._fetch_all_prompts()
            except Exception as e:
                logger.error(f"Error fetching prompts: {e}")
    
    def _fetch_all_prompts(self):
        """Fetch all prompts from the API and update the local cache."""
        try:
            response = self.client.list_prompts(self.project_id)
            prompts_list = response.get("prompts", [])
            
            updated_prompts = []
            
            for prompt_data in prompts_list:
                prompt_name = prompt_data.get("name")
                current_version = prompt_data.get("current_version")
                
                if not prompt_name:
                    continue
                
                with self._lock:
                    last_version = self._last_versions.get(prompt_name)
                
                if last_version is None or last_version < current_version:
                    # Fetch the full prompt data
                    try:
                        full_prompt = self.client.get_prompt(self.project_id, prompt_name)
                        
                        # Update our cache
                        with self._lock:
                            self._prompts[prompt_name] = full_prompt
                            self._last_versions[prompt_name] = current_version
                        
                        updated_prompts.append(prompt_name)
                        
                        # Call the update callback if provided
                        if self.on_update_callback:
                            try:
                                self.on_update_callback(prompt_name, full_prompt)
                            except Exception as e:
                                logger.error(f"Error in update callback for prompt {prompt_name}: {e}")
                    
                    except Exception as e:
                        logger.error(f"Error fetching prompt {prompt_name}: {e}")
            
            if updated_prompts:
                logger.info(f"Updated prompts: {', '.join(updated_prompts)}")
        
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
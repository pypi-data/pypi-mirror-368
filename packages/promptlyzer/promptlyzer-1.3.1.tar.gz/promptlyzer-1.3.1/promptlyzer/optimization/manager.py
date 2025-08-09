"""
Optimization Manager for Promptlyzer

Handles prompt optimization experiments across multiple models.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path

from ..exceptions import (
    PromptlyzerError,
    ValidationError,
    ResourceNotFoundError
)


class OptimizationManager:
    """
    Manager for prompt optimization experiments.
    
    This manager provides:
    - Dataset upload and management
    - Optimization experiment creation
    - Progress monitoring
    - Results retrieval
    """
    
    def __init__(self, promptlyzer_client):
        """
        Initialize the optimization manager.
        
        Args:
            promptlyzer_client: The parent PromptlyzerClient instance
        """
        self.client = promptlyzer_client
        self._experiments = {}  # Cache for experiment tracking
    
    def create(
        self,
        name: str,
        dataset: Union[str, List[Dict[str, str]]],
        system_message: str,
        models: List[Union[str, Dict[str, Any]]],
        project_id: str,
        max_depth: int = 2,
        max_variations: int = 20,
        wait_for_completion: bool = True,
        progress_callback: Optional[Callable[[float], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create and run a prompt optimization experiment.
        
        Args:
            name: Experiment name
            dataset: Path to dataset file (JSON/CSV) or dataset ID starting with "dataset_"
            system_message: The system message to optimize
            models: List of model names or model configurations
            project_id: Project ID
            max_depth: Maximum depth of prompt variations (1-5)
            max_variations: Maximum number of variations to test (5-50)
            wait_for_completion: Whether to wait for experiment to complete
            progress_callback: Optional callback for progress updates
            **kwargs: Additional parameters for the API
            
        Returns:
            Dict containing experiment results if wait_for_completion=True,
            otherwise experiment info with ID
            
        Example:
            >>> result = client.optimization.create(
            ...     name="Support Bot",
            ...     dataset="support_data.json",
            ...     system_message="You are a helpful assistant.",
            ...     models=["gpt-4o", "claude-3.5-sonnet"],
            ...     project_id="proj_123"
            ... )
        """
        # Validate inputs
        if not name or not dataset or not system_message or not models or not project_id:
            raise ValidationError("name, dataset, system_message, models, and project_id are required")
        
        if max_depth < 1 or max_depth > 5:
            raise ValidationError("max_depth must be between 1 and 5")
            
        if max_variations < 3 or max_variations > 50:
            raise ValidationError("max_variations must be between 3 and 50")
        
        # Resolve dataset
        dataset_id = self._resolve_dataset(dataset, project_id)
        
        # Normalize models
        normalized_models = self._normalize_models(models)
        
        # Prepare experiment payload
        payload = {
            "name": name,
            "description": kwargs.get("description", f"Optimization experiment for {name}"),
            "base_prompt": system_message,  # Map system_message to base_prompt
            "dataset_id": dataset_id,
            "max_depth": max_depth,
            "variations_per_level": max_variations,
            "classes": ["answer"],  # Fixed for text experiments
            "task_type": "multi_class",  # Fixed for text experiments
            "use_vision_features": False,  # Always false for text
            "is_multi_model": len(normalized_models) > 1,
            "selected_models": [m["model"] for m in normalized_models],
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 150)
        }
        
        # Ensure project exists
        project_id = self._ensure_project(project_id)
        
        # Create experiment
        url = f"{self.client.api_url}/optimization/experiments?project_id={project_id}"
        headers = self.client.get_headers()
        
        try:
            # No timeout for optimization - can take a long time
            response = self.client._make_request("POST", url, headers=headers, json_data=payload, timeout=None)
            experiment_id = response.get("experiment_id")
            
            # Store experiment info
            self._experiments[experiment_id] = {
                "id": experiment_id,
                "name": name,
                "project_id": project_id,
                "status": response.get("status", "queued")
            }
            
            if wait_for_completion:
                # Wait for experiment to complete
                return self._wait_for_completion(experiment_id, progress_callback)
            else:
                # Return experiment info immediately
                return response
                
        except Exception as e:
            raise PromptlyzerError(f"Failed to create optimization experiment: {str(e)}")
    
    def get_summary(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get summary of an optimization experiment.
        
        Args:
            experiment_id: The experiment ID
            
        Returns:
            Dict containing experiment summary with best results
        """
        url = f"{self.client.api_url}/optimization/experiments/{experiment_id}/brief-summary"
        headers = self.client.get_headers()
        
        try:
            response = self.client._make_request("GET", url, headers=headers)
            
            # Map response fields for consistency
            if "experiment" in response:
                # Extract key metrics
                exp = response["experiment"]
                perf = response.get("performance", {})
                
                # Find best prompt from nodes
                best_prompt = response.get("best_prompt", {}).get("prompt", "")
                
                return {
                    "experiment_id": experiment_id,
                    "status": exp.get("status", "unknown"),
                    "progress": response.get("progress", {}).get("percentage", 0),
                    "best_model": response.get("best_model", {}).get("model"),
                    "best_accuracy": perf.get("best_accuracy", 0),
                    "best_prompt": best_prompt,
                    "total_cost": response.get("cost", {}).get("total_cost_usd", 0),
                    "duration_minutes": exp.get("duration_minutes", 0),
                    "model_comparison": self._extract_model_comparison(response)
                }
            else:
                # Fallback for different response format
                return response
                
        except Exception as e:
            raise PromptlyzerError(f"Failed to get experiment summary: {str(e)}")
    
    def get_details(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get detailed results including prompt evolution tree.
        
        Args:
            experiment_id: The experiment ID
            
        Returns:
            Dict containing the prompt tree structure
        """
        url = f"{self.client.api_url}/optimization/experiments/{experiment_id}/tree"
        headers = self.client.get_headers()
        
        try:
            response = self.client._make_request("GET", url, headers=headers)
            return response
        except Exception as e:
            raise PromptlyzerError(f"Failed to get experiment tree: {str(e)}")
    
    def list_experiments(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List optimization experiments for a project.
        
        Args:
            project_id: The project ID
            limit: Maximum number of experiments to return
            
        Returns:
            List of experiment summaries
        """
        url = f"{self.client.api_url}/optimization/experiments?project_id={project_id}&limit={limit}"
        headers = self.client.get_headers()
        
        try:
            response = self.client._make_request("GET", url, headers=headers)
            return response.get("experiments", [])
        except Exception as e:
            raise PromptlyzerError(f"Failed to list experiments: {str(e)}")
    
    def _resolve_dataset(self, dataset: Union[str, List[Dict[str, str]]], project_id: str) -> str:
        """
        Resolve dataset input to a dataset ID.
        
        Args:
            dataset: File path, dataset ID, or list of data
            project_id: Project ID for dataset upload
            
        Returns:
            Dataset ID
        """
        # Check if it's already a dataset ID
        if isinstance(dataset, str) and dataset.startswith("dataset_"):
            return dataset
        
        # Check if it's a file path
        if isinstance(dataset, str) and (dataset.endswith('.json') or dataset.endswith('.csv')):
            if not os.path.exists(dataset):
                raise ValidationError(f"Dataset file not found: {dataset}")
            
            # Read and validate file
            with open(dataset, 'r') as f:
                if dataset.endswith('.json'):
                    data = json.load(f)
                    if isinstance(data, dict) and 'data' in data:
                        data = data['data']
                    elif isinstance(data, dict) and 'items' in data:
                        data = data['items']
                    
                    if len(data) < 5:
                        raise ValidationError(
                            f"Dataset too small: {len(data)} examples found.\n"
                            f"Minimum 5 examples required for optimization.\n"
                            f"Tip: For better results, consider adding 10-20 diverse examples."
                        )
                else:
                    raise ValidationError("CSV upload not yet implemented. Please use JSON format.")
            
            # Upload dataset
            return self._upload_dataset(dataset, project_id)
        
        # If it's a list, create temporary file and upload
        if isinstance(dataset, list):
            if len(dataset) < 5:
                raise ValidationError(
                    f"Dataset too small: {len(dataset)} examples found.\n"
                    f"Minimum 5 examples required for optimization.\n"
                    f"Tip: For better results, consider adding 10-20 diverse examples."
                )
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(dataset, f)
                temp_path = f.name
            
            try:
                # Upload temporary file
                dataset_id = self._upload_dataset(temp_path, project_id)
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
            
            return dataset_id
        
        raise ValidationError("Dataset must be a file path, dataset ID, or list of examples")
    
    def _upload_dataset(self, file_path: str, project_id: str) -> str:
        """
        Upload a dataset file to the API.
        
        Args:
            file_path: Path to the dataset file
            project_id: Project ID
            
        Returns:
            Dataset ID
        """
        # Ensure project exists before uploading dataset
        project_id = self._ensure_project(project_id)
        
        url = f"{self.client.api_url}/optimization/text/datasets/upload"
        headers = {"X-API-Key": self.client.api_key}  # Don't use JSON content-type for file upload
        
        file_name = os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f, 'application/json')}
            data = {
                'name': f"Dataset {file_name}",
                'description': f"Uploaded via Python client",
                'task_type': 'qa',
                'project_id': project_id
            }
            
            try:
                response = self.client._session.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                result = response.json()
                return result.get('dataset_id')
            except Exception as e:
                raise PromptlyzerError(f"Failed to upload dataset: {str(e)}")
    
    def _normalize_models(self, models: List[Union[str, Dict]]) -> List[Dict[str, Any]]:
        """
        Normalize model inputs to consistent format.
        
        Args:
            models: List of model names or configurations
            
        Returns:
            List of normalized model configurations
        """
        normalized = []
        
        # Model name mappings
        model_mappings = {
            # Common shortcuts
            "gpt-4o": {"provider": "openai", "model": "gpt-4o"},
            "gpt-4-vision": {"provider": "openai", "model": "gpt-4-vision-preview"},
            "gpt-3.5-turbo": {"provider": "openai", "model": "gpt-3.5-turbo"},
            "claude-3.5-sonnet": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            "claude-3-haiku": {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
            "claude-3-opus": {"provider": "anthropic", "model": "claude-3-opus-20240229"},
            "llama-3.3-70b": {"provider": "together", "model": "llama-3.3-70b-turbo"},
            "llama-3.2-3b": {"provider": "together", "model": "llama-3.2-3b"},
            "deepseek-v3": {"provider": "together", "model": "deepseek-v3"},
            # Full names
            "claude-3-5-sonnet-20241022": {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            "llama-3.3-70b-turbo": {"provider": "together", "model": "llama-3.3-70b-turbo"},
        }
        
        for model in models:
            if isinstance(model, str):
                # Look up in mappings
                if model in model_mappings:
                    normalized.append(model_mappings[model])
                else:
                    raise ValidationError(f"Unknown model: {model}")
            elif isinstance(model, dict):
                # Validate dict has required fields
                if "provider" not in model or "model" not in model:
                    raise ValidationError("Model dict must have 'provider' and 'model' fields")
                normalized.append(model)
            else:
                raise ValidationError("Models must be strings or dicts")
        
        return normalized
    
    def _wait_for_completion(
        self, 
        experiment_id: str, 
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        """
        Wait for an experiment to complete.
        
        Args:
            experiment_id: The experiment ID
            progress_callback: Optional callback for progress updates
            
        Returns:
            Final experiment results
        """
        check_interval = 30  # seconds
        max_wait_time = 3600  # 1 hour max
        start_time = time.time()
        
        while True:
            # Get current status
            summary = self.get_summary(experiment_id)
            status = summary.get("status", "unknown")
            progress = summary.get("progress", 0)
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(progress)
            
            # Check if complete
            if status == "completed":
                return summary
            elif status == "failed":
                error_msg = summary.get("error", "Experiment failed")
                raise PromptlyzerError(f"Optimization failed: {error_msg}")
            elif status == "cancelled":
                raise PromptlyzerError("Optimization was cancelled")
            
            # Check timeout
            if time.time() - start_time > max_wait_time:
                raise PromptlyzerError("Optimization timed out after 1 hour")
            
            # Wait before next check
            time.sleep(check_interval)
    
    def _ensure_project(self, project_id: str) -> str:
        """
        Ensure project exists, create if it doesn't.
        
        Args:
            project_id: Project ID or name
            
        Returns:
            Valid project ID
        """
        # First check if project exists
        try:
            url = f"{self.client.api_url}/projects/{project_id}"
            headers = self.client.get_headers()
            self.client._make_request("GET", url, headers=headers)
            # Project exists
            return project_id
        except ResourceNotFoundError:
            # Project doesn't exist, create it
            create_url = f"{self.client.api_url}/projects"
            
            # If project_id looks like an ID (has underscores), use it as name too
            # Otherwise use it as a readable name
            project_name = project_id if not project_id.startswith("proj_") else f"Project {project_id[-6:]}"
            
            payload = {
                "name": project_name,
                "description": f"Auto-created project for optimization",
                "project_type": "text"  # Always text for optimization
            }
            
            try:
                response = self.client._make_request("POST", create_url, headers=headers, json_data=payload)
                new_project_id = response.get("id", response.get("project_id"))
                print(f"✅ Created new project: {project_name} (ID: {new_project_id})")
                return new_project_id
            except Exception as e:
                raise PromptlyzerError(f"Failed to create project: {str(e)}")
        except Exception as e:
            # Some other error - just return original ID
            return project_id
    
    def _extract_model_comparison(self, response: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Extract model comparison data from response.
        
        Args:
            response: API response
            
        Returns:
            Dict mapping model names to their performance metrics
        """
        comparison = {}
        
        # Try to extract from model_performance if available
        if "models" in response:
            for model_info in response["models"]:
                model_name = model_info.get("model")
                if model_name:
                    comparison[model_name] = {
                        "accuracy": model_info.get("best_accuracy", 0),
                        "cost": model_info.get("total_cost", 0),
                        "evaluations": model_info.get("total_evaluations", 0)
                    }
        
        return comparison
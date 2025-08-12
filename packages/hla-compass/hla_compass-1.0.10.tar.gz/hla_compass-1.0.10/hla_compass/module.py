"""
Base module class for HLA-Compass modules
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Union
from pathlib import Path

from .types import ExecutionContext, ModuleInput, ModuleOutput
from .data import PeptideData, ProteinData, SampleData
from .storage import Storage


logger = logging.getLogger(__name__)


class ModuleError(Exception):
    """Base exception for module errors"""
    pass


class ValidationError(ModuleError):
    """Input validation error"""
    pass


class Module(ABC):
    """
    Base class for HLA-Compass modules.
    
    All modules should inherit from this class and implement the execute method.
    """
    
    def __init__(self, manifest_path: str | None = None):
        """
        Initialize module with manifest.
        
        Args:
            manifest_path: Path to manifest.json file
        """
        self.manifest = self._load_manifest(manifest_path)
        self.name = self.manifest.get('name', 'unknown')
        self.version = self.manifest.get('version', '0.0.0')
        self.logger = logging.getLogger(f"hla_compass.module.{self.name}")
        
    def _load_manifest(self, manifest_path: str | None = None) -> dict[str, Any]:
        """Load module manifest from file"""
        if manifest_path is None:
            manifest_path = Path.cwd() / "manifest.json"
        else:
            manifest_path = Path(manifest_path)
            
        if not manifest_path.exists():
            return {}
            
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
            return {}
    
    def run(self, input_data: dict[str, Any], context: ExecutionContext) -> ModuleOutput:
        """
        Main entry point for module execution.
        
        This method handles:
        1. Input validation
        2. Execution
        3. Error handling
        4. Result formatting
        
        Args:
            input_data: Module input parameters
            context: Execution context with API clients
            
        Returns:
            ModuleOutput with results
        """
        start_time = datetime.utcnow()
        
        try:
            # Log execution start
            self.logger.info(
                f"Starting module execution",
                extra={
                    'job_id': context.get('job_id'),
                    'user_id': context.get('user_id'),
                    'organization_id': context.get('organization_id'),
                    'module': self.name,
                    'version': self.version
                }
            )
            
            # Validate inputs
            self.logger.debug("Validating inputs")
            validated_input = self.validate_inputs(input_data)
            
            # Initialize data access helpers
            self._initialize_helpers(context)
            
            # Execute module logic
            self.logger.debug("Executing module logic")
            results = self.execute(validated_input, context)
            
            # Format successful output
            output = self._format_output(
                status='success',
                results=results,
                input_data=validated_input,
                start_time=start_time
            )
            
            self.logger.info(
                f"Module execution completed successfully",
                extra={
                    'job_id': context.get('job_id'),
                    'duration': (datetime.utcnow() - start_time).total_seconds(),
                    'result_count': len(results) if isinstance(results, list) else 1
                }
            )
            
            return output
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return self._format_error(e, 'validation_error', input_data, start_time)
            
        except ModuleError as e:
            self.logger.error(f"Module error: {e}")
            return self._format_error(e, 'module_error', input_data, start_time)
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return self._format_error(e, 'internal_error', input_data, start_time)
    
    def _initialize_helpers(self, context: ExecutionContext):
        """Initialize data access helpers"""
        api_client = context.get('api')
        if api_client:
            self.peptides = PeptideData(api_client)
            self.proteins = ProteinData(api_client)
            self.samples = SampleData(api_client)
            
        storage_client = context.get('storage')
        if storage_client:
            self.storage = Storage(storage_client)
    
    def validate_inputs(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate input data against manifest schema.
        
        Override this method for custom validation logic.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Validated input data
            
        Raises:
            ValidationError: If validation fails
        """
        # Get input schema from manifest
        input_schema = self.manifest.get('inputs', {})
        
        validated = {}
        errors = []
        
        # Check required fields
        for field, schema in input_schema.items():
            if schema.get('required', False) and field not in input_data:
                errors.append(f"Missing required field: {field}")
                continue
                
            if field in input_data:
                value = input_data[field]
                field_type = schema.get('type', 'string')
                
                # Type validation
                if not self._validate_type(value, field_type):
                    errors.append(
                        f"Invalid type for {field}: expected {field_type}, "
                        f"got {type(value).__name__}"
                    )
                    continue
                
                # Additional validation
                if 'min' in schema and value < schema['min']:
                    errors.append(f"{field} must be >= {schema['min']}")
                    
                if 'max' in schema and value > schema['max']:
                    errors.append(f"{field} must be <= {schema['max']}")
                    
                if 'enum' in schema and value not in schema['enum']:
                    errors.append(f"{field} must be one of: {schema['enum']}")
                
                validated[field] = value
            elif 'default' in schema:
                validated[field] = schema['default']
        
        if errors:
            raise ValidationError("; ".join(errors))
            
        return validated
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type"""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True
            
        return isinstance(value, expected)
    
    @abstractmethod
    def execute(self, input_data: dict[str, Any], context: ExecutionContext) -> Any:
        """
        Execute module logic.
        
        This method must be implemented by all modules.
        
        Args:
            input_data: Validated input parameters
            context: Execution context with API clients
            
        Returns:
            Module results (format depends on module)
        """
        pass
    
    def _format_output(self, 
                      status: str,
                      results: Any,
                      input_data: dict[str, Any],
                      start_time: datetime) -> ModuleOutput:
        """Format module output"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Generate summary if not provided
        summary = results.get('summary') if isinstance(results, dict) else None
        if summary is None:
            summary = self._generate_summary(results)
        
        return {
            'status': status,
            'results': results if not isinstance(results, dict) else results.get('results', results),
            'summary': summary,
            'metadata': {
                'module': self.name,
                'version': self.version,
                'execution_time': datetime.utcnow().isoformat() + 'Z',
                'duration_seconds': round(duration, 2),
                'parameters': input_data
            }
        }
    
    def _format_error(self,
                     error: Exception,
                     error_type: str,
                     input_data: dict[str, Any],
                     start_time: datetime) -> ModuleOutput:
        """Format error output"""
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            'status': 'error',
            'error': {
                'type': error_type,
                'message': str(error),
                'details': getattr(error, 'details', None)
            },
            'metadata': {
                'module': self.name,
                'version': self.version,
                'execution_time': datetime.utcnow().isoformat() + 'Z',
                'duration_seconds': round(duration, 2),
                'parameters': input_data
            }
        }
    
    def _generate_summary(self, results: Any) -> dict[str, Any]:
        """Generate default summary from results"""
        if isinstance(results, list):
            return {
                'total_results': len(results),
                'execution_time': datetime.utcnow().isoformat() + 'Z'
            }
        elif isinstance(results, dict):
            return {
                'total_keys': len(results),
                'execution_time': datetime.utcnow().isoformat() + 'Z'
            }
        else:
            return {
                'execution_time': datetime.utcnow().isoformat() + 'Z'
            }
    
    # Convenience methods
    
    def success(self, results: Any, summary: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Create a success response.
        
        Args:
            results: Module results
            summary: Optional summary data
            
        Returns:
            Formatted success response
        """
        output = {'results': results}
        if summary:
            output['summary'] = summary
        return output
    
    def error(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Raise a module error.
        
        Args:
            message: Error message
            details: Optional error details
        """
        error = ModuleError(message)
        if details:
            error.details = details
        raise error
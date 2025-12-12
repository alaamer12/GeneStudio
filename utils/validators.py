"""Validation utilities for input data and parameter checking."""

import re
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging

from utils.error_handling import ValidationError, ErrorContext


class ValidationType(Enum):
    """Types of validation."""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    LENGTH = "length"
    PATTERN = "pattern"
    CUSTOM = "custom"
    FILE = "file"
    SEQUENCE = "sequence"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    rule_type: ValidationType
    message: str
    validator: Optional[Callable[[Any], bool]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    required: bool = False


class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
    
    def add_error(self, field: str, message: str):
        """Add validation error."""
        self.is_valid = False
        self.errors.append({'field': field, 'message': message})
    
    def add_warning(self, field: str, message: str):
        """Add validation warning."""
        self.warnings.append({'field': field, 'message': message})
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages."""
        return [error['message'] for error in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Get all warning messages."""
        return [warning['message'] for warning in self.warnings]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


class Validator:
    """Base validator class."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = {}
    
    def add_rule(self, field: str, rule: ValidationRule):
        """Add validation rule for a field."""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)
    
    def validate(self, data: Dict[str, Any], context: Optional[ErrorContext] = None) -> ValidationResult:
        """Validate data against rules."""
        result = ValidationResult()
        
        # Check required fields
        for field, rules in self.rules.items():
            for rule in rules:
                if rule.required and (field not in data or data[field] is None):
                    result.add_error(field, f"{field} is required")
        
        # Validate present fields
        for field, value in data.items():
            if field in self.rules:
                field_result = self._validate_field(field, value, self.rules[field])
                if not field_result.is_valid:
                    for error in field_result.errors:
                        result.add_error(field, error['message'])
                for warning in field_result.warnings:
                    result.add_warning(field, warning['message'])
        
        return result
    
    def _validate_field(self, field: str, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """Validate a single field."""
        result = ValidationResult()
        
        for rule in rules:
            try:
                if not self._apply_rule(value, rule):
                    result.add_error(field, rule.message)
            except Exception as e:
                self.logger.error(f"Validation rule error for {field}: {e}")
                result.add_error(field, f"Validation error: {e}")
        
        return result
    
    def _apply_rule(self, value: Any, rule: ValidationRule) -> bool:
        """Apply a validation rule."""
        if value is None and not rule.required:
            return True
        
        if rule.rule_type == ValidationType.TYPE:
            return self._validate_type(value, rule)
        elif rule.rule_type == ValidationType.RANGE:
            return self._validate_range(value, rule)
        elif rule.rule_type == ValidationType.LENGTH:
            return self._validate_length(value, rule)
        elif rule.rule_type == ValidationType.PATTERN:
            return self._validate_pattern(value, rule)
        elif rule.rule_type == ValidationType.CUSTOM:
            return rule.validator(value) if rule.validator else True
        elif rule.rule_type == ValidationType.FILE:
            return self._validate_file(value, rule)
        elif rule.rule_type == ValidationType.SEQUENCE:
            return self._validate_sequence(value, rule)
        
        return True
    
    def _validate_type(self, value: Any, rule: ValidationRule) -> bool:
        """Validate value type."""
        expected_type = rule.validator
        if expected_type:
            return isinstance(value, expected_type)
        return True
    
    def _validate_range(self, value: Any, rule: ValidationRule) -> bool:
        """Validate numeric range."""
        try:
            num_value = float(value)
            if rule.min_value is not None and num_value < rule.min_value:
                return False
            if rule.max_value is not None and num_value > rule.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_length(self, value: Any, rule: ValidationRule) -> bool:
        """Validate length constraints."""
        try:
            length = len(value)
            if rule.min_value is not None and length < rule.min_value:
                return False
            if rule.max_value is not None and length > rule.max_value:
                return False
            return True
        except TypeError:
            return False
    
    def _validate_pattern(self, value: Any, rule: ValidationRule) -> bool:
        """Validate regex pattern."""
        if not isinstance(value, str):
            return False
        
        if rule.pattern:
            return bool(re.match(rule.pattern, value))
        
        return True
    
    def _validate_file(self, value: Any, rule: ValidationRule) -> bool:
        """Validate file path."""
        if not isinstance(value, (str, Path)):
            return False
        
        path = Path(value)
        
        # Check if file exists
        if not path.exists():
            return False
        
        # Check if it's a file (not directory)
        if not path.is_file():
            return False
        
        # Check file extension if specified in allowed_values
        if rule.allowed_values:
            file_ext = path.suffix.lower()
            return file_ext in rule.allowed_values
        
        return True
    
    def _validate_sequence(self, value: Any, rule: ValidationRule) -> bool:
        """Validate biological sequence."""
        if not isinstance(value, str):
            return False
        
        sequence = value.upper().strip()
        
        # Check allowed characters if specified
        if rule.allowed_values:
            allowed_chars = set(rule.allowed_values)
            sequence_chars = set(sequence)
            return sequence_chars.issubset(allowed_chars)
        
        return True


class ProjectValidator(Validator):
    """Validator for project data."""
    
    def __init__(self):
        super().__init__()
        self._setup_rules()
    
    def _setup_rules(self):
        """Setup project validation rules."""
        # Project name
        self.add_rule('name', ValidationRule(
            ValidationType.REQUIRED,
            "Project name is required",
            required=True
        ))
        self.add_rule('name', ValidationRule(
            ValidationType.TYPE,
            "Project name must be a string",
            validator=str
        ))
        self.add_rule('name', ValidationRule(
            ValidationType.LENGTH,
            "Project name must be between 2 and 100 characters",
            min_value=2,
            max_value=100
        ))
        self.add_rule('name', ValidationRule(
            ValidationType.PATTERN,
            "Project name contains invalid characters",
            pattern=r'^[^<>:"/\\|?*]+$'
        ))
        
        # Project type
        self.add_rule('type', ValidationRule(
            ValidationType.CUSTOM,
            "Invalid project type",
            validator=lambda x: x in ['sequence_analysis', 'genome_assembly', 'comparative']
        ))
        
        # Description
        self.add_rule('description', ValidationRule(
            ValidationType.LENGTH,
            "Description cannot exceed 1000 characters",
            max_value=1000
        ))
        
        # Status
        self.add_rule('status', ValidationRule(
            ValidationType.CUSTOM,
            "Invalid project status",
            validator=lambda x: x in ['active', 'archived', 'completed']
        ))


class SequenceValidator(Validator):
    """Validator for sequence data."""
    
    def __init__(self):
        super().__init__()
        self._setup_rules()
    
    def _setup_rules(self):
        """Setup sequence validation rules."""
        # Header
        self.add_rule('header', ValidationRule(
            ValidationType.REQUIRED,
            "Sequence header is required",
            required=True
        ))
        self.add_rule('header', ValidationRule(
            ValidationType.TYPE,
            "Header must be a string",
            validator=str
        ))
        self.add_rule('header', ValidationRule(
            ValidationType.LENGTH,
            "Header must be between 1 and 200 characters",
            min_value=1,
            max_value=200
        ))
        
        # Sequence
        self.add_rule('sequence', ValidationRule(
            ValidationType.REQUIRED,
            "Sequence is required",
            required=True
        ))
        self.add_rule('sequence', ValidationRule(
            ValidationType.TYPE,
            "Sequence must be a string",
            validator=str
        ))
        self.add_rule('sequence', ValidationRule(
            ValidationType.LENGTH,
            "Sequence cannot be empty",
            min_value=1
        ))
        self.add_rule('sequence', ValidationRule(
            ValidationType.LENGTH,
            "Sequence is too large (max 10 million characters)",
            max_value=10000000
        ))
        
        # Sequence type
        self.add_rule('sequence_type', ValidationRule(
            ValidationType.CUSTOM,
            "Invalid sequence type",
            validator=lambda x: x in ['dna', 'rna', 'protein']
        ))
    
    def validate_sequence_content(self, sequence: str, sequence_type: str) -> ValidationResult:
        """Validate sequence content based on type."""
        result = ValidationResult()
        
        if not sequence:
            result.add_error('sequence', "Sequence cannot be empty")
            return result
        
        sequence = sequence.upper().strip()
        
        if sequence_type == 'dna':
            valid_chars = set('ATCGN')
            invalid_chars = set(sequence) - valid_chars
            if invalid_chars:
                result.add_error('sequence', f"Invalid DNA characters: {invalid_chars}")
        
        elif sequence_type == 'rna':
            valid_chars = set('AUCGN')
            invalid_chars = set(sequence) - valid_chars
            if invalid_chars:
                result.add_error('sequence', f"Invalid RNA characters: {invalid_chars}")
        
        elif sequence_type == 'protein':
            valid_chars = set('ACDEFGHIKLMNPQRSTVWYX*')
            invalid_chars = set(sequence) - valid_chars
            if invalid_chars:
                result.add_error('sequence', f"Invalid protein characters: {invalid_chars}")
        
        return result


class FileValidator(Validator):
    """Validator for file operations."""
    
    def __init__(self):
        super().__init__()
        self._setup_rules()
    
    def _setup_rules(self):
        """Setup file validation rules."""
        # File path
        self.add_rule('filepath', ValidationRule(
            ValidationType.REQUIRED,
            "File path is required",
            required=True
        ))
        self.add_rule('filepath', ValidationRule(
            ValidationType.FILE,
            "File does not exist or is not accessible"
        ))
    
    def validate_fasta_file(self, filepath: str) -> ValidationResult:
        """Validate FASTA file format and content."""
        result = ValidationResult()
        
        # Check file exists
        if not Path(filepath).exists():
            result.add_error('filepath', f"File not found: {filepath}")
            return result
        
        # Check file extension
        valid_extensions = {'.fasta', '.fa', '.fas', '.fna'}
        file_ext = Path(filepath).suffix.lower()
        if file_ext not in valid_extensions:
            result.add_warning('filepath', f"Unusual file extension: {file_ext}")
        
        # Check file size (limit to 100MB)
        try:
            file_size = Path(filepath).stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                result.add_error('filepath', "File is too large (max 100MB)")
                return result
        except OSError as e:
            result.add_error('filepath', f"Cannot access file: {e}")
            return result
        
        # Validate FASTA format
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                line_count = 0
                sequence_count = 0
                in_sequence = False
                current_sequence = ""
                
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    if line.startswith('>'):
                        # Header line
                        if in_sequence and current_sequence:
                            sequence_count += 1
                        in_sequence = True
                        current_sequence = ""
                        
                        # Validate header
                        if len(line) < 2:
                            result.add_error('format', f"Empty header at line {line_num}")
                    
                    elif in_sequence:
                        # Sequence line
                        current_sequence += line
                        
                        # Basic sequence validation
                        if not re.match(r'^[A-Za-z\-\*\n\r\s]*$', line):
                            result.add_warning('format', f"Unusual characters in sequence at line {line_num}")
                    
                    else:
                        # Line before first header
                        result.add_error('format', f"Content before first header at line {line_num}")
                    
                    # Limit line checking to prevent memory issues
                    if line_count > 10000:
                        break
                
                # Check final sequence
                if in_sequence and current_sequence:
                    sequence_count += 1
                
                if sequence_count == 0:
                    result.add_error('format', "No valid sequences found in file")
        
        except UnicodeDecodeError:
            result.add_error('format', "File encoding error - not a valid text file")
        except Exception as e:
            result.add_error('format', f"Error reading file: {e}")
        
        return result


class AnalysisValidator(Validator):
    """Validator for analysis parameters."""
    
    def __init__(self):
        super().__init__()
        self._setup_rules()
    
    def _setup_rules(self):
        """Setup analysis validation rules."""
        # Analysis type
        self.add_rule('analysis_type', ValidationRule(
            ValidationType.REQUIRED,
            "Analysis type is required",
            required=True
        ))
        
        # Parameters
        self.add_rule('parameters', ValidationRule(
            ValidationType.TYPE,
            "Parameters must be a dictionary",
            validator=dict
        ))
    
    def validate_pattern_matching_params(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate pattern matching parameters."""
        result = ValidationResult()
        
        # Pattern
        if 'pattern' not in params:
            result.add_error('pattern', "Pattern is required")
        else:
            pattern = params['pattern']
            if not isinstance(pattern, str) or not pattern.strip():
                result.add_error('pattern', "Pattern must be a non-empty string")
            elif len(pattern) > 1000:
                result.add_error('pattern', "Pattern is too long (max 1000 characters)")
        
        # Algorithm
        if 'algorithm' in params:
            valid_algorithms = ['boyer_moore', 'naive', 'kmp']
            if params['algorithm'] not in valid_algorithms:
                result.add_error('algorithm', f"Invalid algorithm. Must be one of: {valid_algorithms}")
        
        # Case sensitive
        if 'case_sensitive' in params:
            if not isinstance(params['case_sensitive'], bool):
                result.add_error('case_sensitive', "case_sensitive must be a boolean")
        
        return result
    
    def validate_translation_params(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate translation parameters."""
        result = ValidationResult()
        
        # Reading frame
        if 'frame' in params:
            frame = params['frame']
            if not isinstance(frame, int) or frame not in [0, 1, 2]:
                result.add_error('frame', "Reading frame must be 0, 1, or 2")
        
        # Genetic code
        if 'genetic_code' in params:
            valid_codes = ['standard', 'vertebrate_mitochondrial', 'yeast_mitochondrial']
            if params['genetic_code'] not in valid_codes:
                result.add_error('genetic_code', f"Invalid genetic code. Must be one of: {valid_codes}")
        
        return result


class ValidationManager:
    """Manager for all validation operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validators = {
            'project': ProjectValidator(),
            'sequence': SequenceValidator(),
            'file': FileValidator(),
            'analysis': AnalysisValidator()
        }
    
    def validate_project(self, project_data: Dict[str, Any], 
                        context: Optional[ErrorContext] = None) -> ValidationResult:
        """Validate project data."""
        return self.validators['project'].validate(project_data, context)
    
    def validate_sequence(self, sequence_data: Dict[str, Any],
                         context: Optional[ErrorContext] = None) -> ValidationResult:
        """Validate sequence data."""
        result = self.validators['sequence'].validate(sequence_data, context)
        
        # Additional sequence content validation
        if 'sequence' in sequence_data and 'sequence_type' in sequence_data:
            content_result = self.validators['sequence'].validate_sequence_content(
                sequence_data['sequence'],
                sequence_data['sequence_type']
            )
            
            # Merge results
            for error in content_result.errors:
                result.add_error(error['field'], error['message'])
            for warning in content_result.warnings:
                result.add_warning(warning['field'], warning['message'])
        
        return result
    
    def validate_fasta_file(self, filepath: str,
                           context: Optional[ErrorContext] = None) -> ValidationResult:
        """Validate FASTA file."""
        return self.validators['file'].validate_fasta_file(filepath)
    
    def validate_analysis_parameters(self, analysis_type: str, params: Dict[str, Any],
                                   context: Optional[ErrorContext] = None) -> ValidationResult:
        """Validate analysis parameters."""
        validator = self.validators['analysis']
        
        # Basic validation
        data = {'analysis_type': analysis_type, 'parameters': params}
        result = validator.validate(data, context)
        
        # Type-specific validation
        if analysis_type == 'pattern_matching':
            type_result = validator.validate_pattern_matching_params(params)
        elif analysis_type == 'translation':
            type_result = validator.validate_translation_params(params)
        else:
            type_result = ValidationResult()  # No specific validation
        
        # Merge results
        for error in type_result.errors:
            result.add_error(error['field'], error['message'])
        for warning in type_result.warnings:
            result.add_warning(warning['field'], warning['message'])
        
        return result
    
    def validate_and_raise(self, validation_result: ValidationResult, 
                          context: Optional[ErrorContext] = None):
        """Validate result and raise ValidationError if invalid."""
        if not validation_result.is_valid:
            error_messages = validation_result.get_error_messages()
            raise ValidationError(
                f"Validation failed: {'; '.join(error_messages)}",
                context=context
            )


# Global validation manager
_validation_manager = ValidationManager()


def get_validation_manager() -> ValidationManager:
    """Get the global validation manager."""
    return _validation_manager


# Convenience functions
def validate_project(project_data: Dict[str, Any]) -> ValidationResult:
    """Validate project data."""
    return _validation_manager.validate_project(project_data)


def validate_sequence(sequence_data: Dict[str, Any]) -> ValidationResult:
    """Validate sequence data."""
    return _validation_manager.validate_sequence(sequence_data)


def validate_fasta_file(filepath: str) -> ValidationResult:
    """Validate FASTA file."""
    return _validation_manager.validate_fasta_file(filepath)


def validate_analysis_parameters(analysis_type: str, params: Dict[str, Any]) -> ValidationResult:
    """Validate analysis parameters."""
    return _validation_manager.validate_analysis_parameters(analysis_type, params)


def validate_and_raise(validation_result: ValidationResult, context: Optional[ErrorContext] = None):
    """Validate result and raise ValidationError if invalid."""
    _validation_manager.validate_and_raise(validation_result, context)


# Specific validation functions
def validate_dna_sequence(sequence: str) -> bool:
    """Validate DNA sequence characters."""
    if not sequence:
        return False
    
    valid_chars = set('ATCGN')
    return set(sequence.upper()) <= valid_chars


def validate_rna_sequence(sequence: str) -> bool:
    """Validate RNA sequence characters."""
    if not sequence:
        return False
    
    valid_chars = set('AUCGN')
    return set(sequence.upper()) <= valid_chars


def validate_protein_sequence(sequence: str) -> bool:
    """Validate protein sequence characters."""
    if not sequence:
        return False
    
    valid_chars = set('ACDEFGHIKLMNPQRSTVWYX*')
    return set(sequence.upper()) <= valid_chars


def validate_file_path(filepath: str, must_exist: bool = True) -> bool:
    """Validate file path."""
    try:
        path = Path(filepath)
        
        if must_exist:
            return path.exists() and path.is_file()
        else:
            # Check if parent directory exists
            return path.parent.exists()
    
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure not empty
    if not filename:
        filename = 'untitled'
    
    return filename


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize text input."""
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text
"""
Type definitions for HLA-Compass SDK
"""

from typing import Any, Union, TypedDict, Literal
from enum import Enum
from datetime import datetime


# Execution context type
class ExecutionContext(TypedDict):
    """Execution context provided to modules"""
    job_id: str
    user_id: str
    organization_id: str
    api: Any  # API client instance
    storage: Any  # Storage client instance
    tier: Literal['foundational', 'advanced', 'strategic']
    execution_time: datetime


# Module types
ModuleInput = dict[str, Any]
ModuleOutput = dict[str, Any]


# Job status enum
class JobStatus(str, Enum):
    """Job execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Compute type enum
class ComputeType(str, Enum):
    """Module compute type"""
    LAMBDA = "lambda"
    FARGATE = "fargate"
    SAGEMAKER = "sagemaker"


# Module type enum
class ModuleType(str, Enum):
    """Module UI type"""
    NO_UI = "no-ui"
    WITH_UI = "with-ui"


# Data types
class Peptide(TypedDict):
    """Peptide data structure"""
    id: str
    sequence: str
    length: int
    mass: float
    charge: int | None
    modifications: list[str] | None
    metadata: dict[str, Any] | None


class Protein(TypedDict):
    """Protein data structure"""
    id: str
    accession: str
    gene_name: str | None
    organism: str
    sequence: str
    length: int
    description: str | None
    metadata: dict[str, Any] | None


class Sample(TypedDict):
    """Sample data structure"""
    id: str
    name: str
    sample_type: str
    tissue: str | None
    disease: str | None
    cell_line: str | None
    treatment: str | None
    experiment_type: str
    metadata: dict[str, Any] | None


class PeptideSample(TypedDict):
    """Peptide-sample association"""
    peptide_id: str
    sample_id: str
    abundance: float
    confidence: float | None
    metadata: dict[str, Any] | None


# API response types
class APIResponse(TypedDict):
    """Standard API response"""
    status: Literal['success', 'error']
    data: Any | None
    error: dict[str, Any] | None
    metadata: dict[str, Any] | None


class PaginatedResponse(TypedDict):
    """Paginated API response"""
    results: list[Any]
    total: int
    limit: int
    offset: int
    has_more: bool


# Module manifest types
class ManifestAuthor(TypedDict):
    """Module author information"""
    name: str
    email: str
    organization: str | None


class ManifestInputField(TypedDict, total=False):
    """Input field definition"""
    type: str
    required: bool
    description: str
    default: Any
    min: Union[int, float] | None
    max: Union[int, float] | None
    enum: list[Any] | None


class ManifestComputeRequirements(TypedDict):
    """Compute requirements"""
    memory: int  # MB
    timeout: int  # seconds
    environment: str  # e.g., "python3.11"
    gpu: bool | None


class ModuleManifest(TypedDict):
    """Module manifest structure"""
    name: str
    version: str
    displayName: str
    description: str
    author: ManifestAuthor
    type: Literal['no-ui', 'with-ui']
    computeType: Literal['lambda', 'fargate', 'sagemaker']
    computeRequirements: ManifestComputeRequirements
    inputs: dict[str, ManifestInputField]
    outputs: dict[str, Any]
    dependencies: dict[str, list[str]]
    permissions: dict[str, list[str]]
    tags: list[str]
    category: str
    pricing: dict[str, Any] | None
    support: dict[str, str] | None


# Error types
class ErrorDetail(TypedDict):
    """Error detail structure"""
    code: str
    message: str
    field: str | None
    details: dict[str, Any] | None


# Storage types
class StorageObject(TypedDict):
    """Storage object metadata"""
    key: str
    size: int
    last_modified: datetime
    content_type: str
    etag: str | None
    metadata: dict[str, str] | None


# HLA-specific types
HLAAllele = str  # e.g., "HLA-A*02:01"
HLALocus = Literal['A', 'B', 'C', 'DRB1', 'DRB3', 'DRB4', 'DRB5', 'DQA1', 'DQB1', 'DPA1', 'DPB1']


class HLAPrediction(TypedDict):
    """HLA binding prediction result"""
    peptide: str
    allele: HLAAllele
    score: float
    rank: float
    binding_category: Literal['strong', 'weak', 'non-binder']
    method: str


# Execution types
class ExecutionOptions(TypedDict, total=False):
    """Module execution options"""
    priority: Literal['low', 'normal', 'high']
    timeout: int
    memory: int
    notifications: bool
    webhook_url: str | None


class ExecutionResult(TypedDict):
    """Module execution result"""
    job_id: str
    status: JobStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: ModuleOutput | None
    error: ErrorDetail | None
    metadata: dict[str, Any]
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DataSourceInfo(BaseModel):
    """Information about the data source for a document."""

    model_config = ConfigDict(extra='ignore')

    upload_file_id: Optional[str] = Field(None, description="ID of uploaded file")


class ProcessRule(BaseModel):
    """Processing rules for document indexing."""

    model_config = ConfigDict(extra='ignore')

    mode: Literal["automatic", "custom"] = Field(description="Processing mode")
    rules: Optional[Dict[str, Any]] = Field(None, description="Custom processing rules")


class PreProcessingRule(BaseModel):
    """Preprocessing rule configuration."""

    model_config = ConfigDict(extra='ignore')

    id: str = Field(description="Rule ID")
    enabled: bool = Field(description="Whether the rule is enabled")


class Segmentation(BaseModel):
    """Text segmentation configuration."""

    model_config = ConfigDict(extra='ignore')

    separator: str = Field(description="Segment separator")
    max_tokens: int = Field(description="Maximum tokens per segment", gt=0, le=4096)


class ProcessRuleConfig(BaseModel):
    """Process rule configuration."""

    model_config = ConfigDict(extra='ignore')

    pre_processing_rules: List[PreProcessingRule] = Field(description="Preprocessing rules")
    segmentation: Segmentation = Field(description="Segmentation configuration")


class Document(BaseModel):
    """Document information in a dataset."""

    model_config = ConfigDict(extra='ignore')

    id: str = Field(description="Document ID")
    position: int = Field(description="Document position", ge=0)
    data_source_type: str = Field(description="Data source type")
    data_source_info: Optional[DataSourceInfo] = Field(None, description="Data source info")
    dataset_process_rule_id: Optional[str] = Field(None, description="Process rule ID")
    name: str = Field(description="Document name", min_length=1)
    created_from: str = Field(description="Creation source")
    created_by: str = Field(description="Creator ID")
    created_at: int = Field(description="Creation timestamp", ge=0)
    tokens: int = Field(description="Token count", ge=0)
    indexing_status: str = Field(description="Indexing status")
    error: Optional[str] = Field(None, description="Error message")
    enabled: bool = Field(description="Whether document is enabled")
    disabled_at: Optional[int] = Field(None, description="Disabled timestamp")
    disabled_by: Optional[str] = Field(None, description="User who disabled")
    archived: bool = Field(description="Whether document is archived")
    display_status: Optional[str] = Field(None, description="Display status")
    word_count: int = Field(description="Word count", ge=0)
    hit_count: int = Field(description="Hit count", ge=0)
    doc_form: str = Field(description="Document form")


class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    provider: Optional[str] = None
    permission: str
    data_source_type: Optional[str] = None
    indexing_technique: Optional[str] = None
    app_count: int
    document_count: int
    word_count: int
    created_by: str
    created_at: int
    updated_by: str
    updated_at: int
    embedding_model: Optional[str] = None
    embedding_model_provider: Optional[str] = None
    embedding_available: Optional[bool] = None


class Segment(BaseModel):
    id: str
    position: int
    document_id: str
    content: str
    answer: Optional[str] = None
    word_count: int
    tokens: int
    keywords: Optional[List[str]] = None
    index_node_id: str
    index_node_hash: str
    hit_count: int
    enabled: bool
    disabled_at: Optional[int] = None
    disabled_by: Optional[str] = None
    status: str
    created_by: str
    created_at: int
    indexing_at: int
    completed_at: Optional[int] = None
    error: Optional[str] = None
    stopped_at: Optional[int] = None


class IndexingStatus(BaseModel):
    id: str
    indexing_status: str
    processing_started_at: Optional[float] = None
    parsing_completed_at: Optional[float] = None
    cleaning_completed_at: Optional[float] = None
    splitting_completed_at: Optional[float] = None
    completed_at: Optional[float] = None
    paused_at: Optional[float] = None
    error: Optional[str] = None
    stopped_at: Optional[float] = None
    completed_segments: int
    total_segments: int


class Metadata(BaseModel):
    id: str
    type: str
    name: str
    use_count: Optional[int] = None


class MetadataValue(BaseModel):
    id: str
    value: str
    name: str


class DocumentMetadata(BaseModel):
    document_id: str
    metadata_list: List[MetadataValue]


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""

    model_config = ConfigDict(extra='ignore')

    data: List[Any] = Field(description="Response data items")
    has_more: bool = Field(description="Whether more pages are available")
    limit: int = Field(description="Items per page limit", gt=0, le=100)
    total: int = Field(description="Total number of items", ge=0)
    page: int = Field(description="Current page number", gt=0)


class CreateDocumentByTextRequest(BaseModel):
    name: str
    text: str
    indexing_technique: str = "high_quality"
    process_rule: ProcessRule


class CreateDocumentByFileRequest(BaseModel):
    indexing_technique: str = "high_quality"
    process_rule: ProcessRule


class CreateDatasetRequest(BaseModel):
    """Request model for creating a new dataset."""

    model_config = ConfigDict(extra='ignore')

    name: str = Field(description="Dataset name", min_length=1, max_length=100)
    permission: Literal["only_me", "all_team_members"] = Field("only_me", description="Dataset permission level")
    description: Optional[str] = Field(None, description="Dataset description", max_length=500)


class UpdateDocumentByTextRequest(BaseModel):
    name: str
    text: str


class CreateSegmentRequest(BaseModel):
    segments: List[Dict[str, Any]]


class UpdateSegmentRequest(BaseModel):
    segment: Dict[str, Any]


class CreateMetadataRequest(BaseModel):
    type: str
    name: str


class UpdateMetadataRequest(BaseModel):
    name: str


class DocumentMetadataRequest(BaseModel):
    operation_data: List[DocumentMetadata]


class DocumentResponse(BaseModel):
    document: Document
    batch: str


class SegmentResponse(BaseModel):
    data: List[Segment]
    doc_form: str


class MetadataListResponse(BaseModel):
    doc_metadata: List[Metadata]
    built_in_field_enabled: bool


class IndexingStatusResponse(BaseModel):
    data: List[IndexingStatus]


class SuccessResponse(BaseModel):
    """Standard success response model."""

    model_config = ConfigDict(extra='ignore')

    result: Literal["success"] = Field("success", description="Operation result status")

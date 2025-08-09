from __future__ import annotations

import sys as _sys

from .core import (
    Edge,
    Message,
    MessageType,
    Node,
    Port,
    PortDirection,
    Scheduler,
    SchedulerConfig,
    Subgraph,
)
from .nodes import (
    FunctionNode,
    ErrorPolicy,
    MergeStrategy,
    DistributionStrategy,
    NodeConfig,
    TimingConfig,
    create_error_message,
    validate_callable,
    setup_standard_ports,
    NodeTestHarness,
    # Basic nodes
    DataProducer,
    BatchProducer,
    DataConsumer,
    BatchConsumer,
    MapTransformer,
    FilterTransformer,
    FlatMapTransformer,
    Router,
    Merger,
    Splitter,
    EventAggregator,
    EventCorrelator,
    TriggerNode,
    WorkerPool,
    AsyncWorker,
    CacheNode,
    BufferNode,
    FileWriterNode,
    FileReaderNode,
    HttpClientNode,
    HttpServerNode,
    WebSocketNode,
    MessageQueueNode,
    MetricsCollectorNode,
    HealthCheckNode,
    AlertingNode,
    SamplingNode,
    ValidationNode,
    SerializationNode,
    CompressionNode,
    EncryptionNode,
    SchemaType,
    SerializationFormat,
    CompressionType,
    CompressionMode,
    EncryptionAlgorithm,
    EncryptionMode,
    ThrottleNode,
    CircuitBreakerNode,
    RetryNode,
    TimeoutNode,
    RateLimitAlgorithm,
    BackoffStrategy,
    TimeoutAction,
    StateMachineNode,
    SessionNode,
    CounterNode,
    WindowNode,
    WindowType,
)

__all__ = [
    "__version__",
    "core",
    "observability",
    "utils",
    # Convenience re-exports
    "Message",
    "MessageType",
    "Node",
    "Subgraph",
    "Edge",
    "Port",
    "PortDirection",
    "Scheduler",
    "SchedulerConfig",
    # Built-in nodes base exports
    "FunctionNode",
    "ErrorPolicy",
    "MergeStrategy",
    "DistributionStrategy",
    "NodeConfig",
    "TimingConfig",
    "create_error_message",
    "validate_callable",
    "setup_standard_ports",
    "NodeTestHarness",
    # Basic nodes
    "DataProducer",
    "BatchProducer",
    "DataConsumer",
    "BatchConsumer",
    "MapTransformer",
    "FilterTransformer",
    "FlatMapTransformer",
    # Controllers
    "Router",
    "Merger",
    "Splitter",
    # Events
    "EventAggregator",
    "EventCorrelator",
    "TriggerNode",
    # Workers
    "WorkerPool",
    "AsyncWorker",
    # Storage
    "CacheNode",
    "BufferNode",
    "FileWriterNode",
    "FileReaderNode",
    # Network
    "HttpClientNode",
    "HttpServerNode",
    "WebSocketNode",
    "MessageQueueNode",
    # Monitoring
    "MetricsCollectorNode",
    "HealthCheckNode",
    "AlertingNode",
    "SamplingNode",
    # Data processing
    "ValidationNode",
    "SerializationNode",
    "CompressionNode",
    "EncryptionNode",
    "SchemaType",
    "SerializationFormat",
    "CompressionType",
    "CompressionMode",
    "EncryptionAlgorithm",
    "EncryptionMode",
    # Flow control
    "ThrottleNode",
    "CircuitBreakerNode",
    "RetryNode",
    "TimeoutNode",
    "RateLimitAlgorithm",
    "BackoffStrategy",
    "TimeoutAction",
    # State management
    "StateMachineNode",
    "SessionNode",
    "CounterNode",
    "WindowNode",
    "WindowType",
]

__version__ = "0.0.0"

_PKG_NAME = "meridian"
_MIN_PY = (3, 11)

if _sys.version_info < _MIN_PY:
    raise RuntimeError(
        f"{_PKG_NAME} requires Python {'.'.join(map(str, _MIN_PY))}+; "
        f"detected {_sys.version.split()[0]}"
    )

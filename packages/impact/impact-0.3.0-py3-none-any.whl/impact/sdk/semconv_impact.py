"""
Local implementation of ImpactSpanKindValues and SpanAttributes.

This module provides local versions of classes that were previously imported 
from opentelemetry.semconv_ai. By maintaining our own implementation, we have 
more control over these critical components without external dependencies.

The SpanAttributes class inherits from the OpenTelemetry version to ensure
compatibility while allowing us to add our own attributes.
"""

from enum import Enum
from opentelemetry.semconv_ai import SpanAttributes as OTelSpanAttributes


class ImpactSpanKindValues(Enum):
    WORKFLOW = "workflow"
    TASK = "task"
    AGENT = "agent"
    TOOL = "tool"
    UNKNOWN = "unknown"


class SpanAttributes(OTelSpanAttributes):
    # Impact specific attributes
    IMPACT_SPAN_KIND = "impact.span.kind"
    IMPACT_WORKFLOW_NAME = "impact.workflow.name"
    IMPACT_ENTITY_NAME = "impact.entity.name"
    IMPACT_ENTITY_PATH = "impact.entity.path"
    IMPACT_ENTITY_VERSION = "impact.entity.version"
    IMPACT_ENTITY_INPUT = "impact.entity.input"
    IMPACT_ENTITY_OUTPUT = "impact.entity.output"
    IMPACT_ASSOCIATION_PROPERTIES = "impact.association.properties"

    # Prompts
    IMPACT_PROMPT_MANAGED = "impact.prompt.managed"
    IMPACT_PROMPT_KEY = "impact.prompt.key"
    IMPACT_PROMPT_VERSION = "impact.prompt.version"
    IMPACT_PROMPT_VERSION_NAME = "impact.prompt.version_name"
    IMPACT_PROMPT_VERSION_HASH = "impact.prompt.version_hash"
    IMPACT_PROMPT_TEMPLATE = "impact.prompt.template"
    IMPACT_PROMPT_TEMPLATE_VARIABLES = "impact.prompt.template_variables"

    # Deprecated
    IMPACT_CORRELATION_ID = "impact.correlation.id" 
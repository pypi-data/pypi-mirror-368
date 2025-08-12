from typing import Optional
import warnings

from impact.sdk.semconv_impact import ImpactSpanKindValues

from impact.sdk.decorators.base import (
    entity_class,
    entity_method,
)


def task(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[ImpactSpanKindValues] = ImpactSpanKindValues.TASK,
):
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
        )


def workflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[ImpactSpanKindValues] = ImpactSpanKindValues.WORKFLOW,
):
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
        )


def agent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    return workflow(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=ImpactSpanKindValues.AGENT,
    )


def tool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    return task(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=ImpactSpanKindValues.TOOL,
    )


# Async Decorators - Deprecated
def atask(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[ImpactSpanKindValues] = ImpactSpanKindValues.TASK,
):
    warnings.warn(
        "DeprecationWarning: The @atask decorator will be removed in a future version. "
        "Please migrate to @task for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2
    )
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(name=name, version=version, method_name=method_name, tlp_span_kind=tlp_span_kind)


def aworkflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[ImpactSpanKindValues] = ImpactSpanKindValues.WORKFLOW,
):
    warnings.warn(
        "DeprecationWarning: The @aworkflow decorator will be removed in a future version. "
        "Please migrate to @workflow for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2
    )
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
        )


def aagent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    warnings.warn(
        "DeprecationWarning: The @aagent decorator will be removed in a future version. "
        "Please migrate to @agent for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2
    )
    return atask(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=ImpactSpanKindValues.AGENT,
    )


def atool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
):
    warnings.warn(
        "DeprecationWarning: The @atool decorator will be removed in a future version. "
        "Please migrate to @tool for both sync and async operations.",
        DeprecationWarning,
        stacklevel=2
    )
    return atask(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=ImpactSpanKindValues.TOOL,
    )

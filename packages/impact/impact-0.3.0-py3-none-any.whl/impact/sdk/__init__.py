import os
import sys
from pathlib import Path

from typing import Optional, Set
from colorama import Fore
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter


from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.propagators.textmap import TextMapPropagator
from opentelemetry.util.re import parse_env_headers

from impact.sdk.images.image_uploader import ImageUploader


from impact.sdk.telemetry import Telemetry
from impact.sdk.instruments import Instruments
from impact.sdk.config import (
    is_content_tracing_enabled,
    is_tracing_enabled,


)
from impact.sdk.fetcher import Fetcher
from impact.sdk.tracing.tracing import (
    TracerWrapper,
    set_association_properties,
    set_external_prompt_tracing_context,
)
from typing import Dict
from impact.sdk.client.client import Client


class Impact:
    AUTO_CREATED_KEY_PATH = str(
        Path.home() / ".cache" / "impact" / "auto_created_key"
    )
    AUTO_CREATED_URL = str(Path.home() / ".cache" / "impact" / "auto_created_url")

    __tracer_wrapper: TracerWrapper
    __fetcher: Optional[Fetcher] = None
    __app_name: Optional[str] = None
    __client: Optional[Client] = None

    @staticmethod
    def init(
        app_name: str = sys.argv[0],
        api_endpoint: str = "https://api.impact.ai",
        api_key: Optional[str] = None,
        enabled: bool = True,
        headers: Dict[str, str] = {},
        disable_batch=False,
        telemetry_enabled: bool = False,
        exporter: Optional[SpanExporter] = None,
        
        
        
        
        processor: Optional[SpanProcessor] = None,
        propagator: TextMapPropagator = None,
        impact_sync_enabled: bool = False,
        
        resource_attributes: dict = {},
        instruments: Optional[Set[Instruments]] = None,
        block_instruments: Optional[Set[Instruments]] = None,
        image_uploader: Optional[ImageUploader] = None,
    ) -> Optional[Client]:
        if not enabled:
            TracerWrapper.set_disabled(True)
            print(
                Fore.YELLOW
                + "Impact instrumentation is disabled via init flag"
                + Fore.RESET
            )
            return

        telemetry_enabled = (
            telemetry_enabled
            and (os.getenv("IMPACT_TELEMETRY") or "true").lower() == "true"
        )
        if telemetry_enabled:
            Telemetry()

        api_endpoint = os.getenv("IMPACT_BASE_URL") or api_endpoint
        api_key = os.getenv("IMPACT_API_KEY") or api_key
        Impact.__app_name = app_name

        if not is_tracing_enabled():
            print(Fore.YELLOW + "Tracing is disabled" + Fore.RESET)
            return

        enable_content_tracing = is_content_tracing_enabled()

        if exporter or processor:
            print(Fore.GREEN + "Impact exporting traces to a custom exporter")

        headers = os.getenv("IMPACT_HEADERS") or headers

        if isinstance(headers, str):
            headers = parse_env_headers(headers)

        if (
            not exporter
            and not processor
            and api_endpoint == "https://api.impact.ai"
            and not api_key
        ):
            print(
                Fore.RED
                + "Error: Missing Impact API key,"
                + " go to https://app.impact.ai/settings/api-keys to create one"
            )
            print("Set the IMPACT_API_KEY environment variable to the key")
            print(Fore.RESET)
            return

        if not exporter and not processor and headers:
            print(
                Fore.GREEN
                + f"Impact exporting traces to {api_endpoint}, authenticating with custom headers"
            )

        if api_key and not exporter and not processor and not headers:
            print(
                Fore.GREEN
                + f"Impact exporting traces to {api_endpoint} authenticating with bearer token"
            )
            headers = {
                "Authorization": f"Bearer {api_key}",
            }

        print(Fore.RESET)

        # Tracer init
        resource_attributes.update({SERVICE_NAME: app_name})
        TracerWrapper.set_static_params(
            resource_attributes, enable_content_tracing, api_endpoint, headers
        )
        Impact.__tracer_wrapper = TracerWrapper(
            disable_batch=disable_batch,
            processor=processor,
            propagator=propagator,
            exporter=exporter,

            image_uploader=image_uploader or ImageUploader(api_endpoint, api_key),
            instruments=instruments,
            block_instruments=block_instruments,
        )



        if (
            api_endpoint.find("impact.ai") != -1
            and api_key
            and (exporter is None)
            and (processor is None)
        ):
            if impact_sync_enabled:
                Impact.__fetcher = Fetcher(base_url=api_endpoint, api_key=api_key)
                Impact.__fetcher.run()
                print(
                    Fore.GREEN
                    + "Impact syncing configuration and prompts"
                    + Fore.RESET
                )
            Impact.__client = Client(
                api_key=api_key, app_name=app_name, api_endpoint=api_endpoint
            )
            return Impact.__client

    def set_association_properties(properties: dict) -> None:
        set_association_properties(properties)

    def set_prompt(template: str, variables: dict, version: int):
        set_external_prompt_tracing_context(template, variables, version)

    @staticmethod
    def get():
        """
        Returns the shared SDK client instance, using the current global configuration.

        To use the SDK as a singleton, first make sure you have called :func:`Impact.init()`
        at startup time. Then ``get()`` will return the same shared :class:`Impact.client.Client`
        instance each time. The client will be initialized if it has not been already.

        If you need to create multiple client instances with different configurations, instead of this
        singleton approach you can call the :class:`Impact.client.Client` constructor directly instead.
        """
        if not Impact.__client:
            raise Exception(
                "Client not initialized, you should call Impact.init() first. "
                "If you are still getting this error - you are missing the api key"
            )
        return Impact.__client

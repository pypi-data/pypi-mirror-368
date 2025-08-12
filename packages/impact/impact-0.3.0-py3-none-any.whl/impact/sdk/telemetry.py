# Stubbed telemetry module - does not collect or send any data
class Telemetry:
    def __new__(cls) -> "Telemetry":
        if not hasattr(cls, "instance"):
            obj = cls.instance = super(Telemetry, cls).__new__(cls)
            obj._telemetry_enabled = False
        return cls.instance

    def capture(self, event: str, event_properties: dict = {}) -> None:
        # Stub - does nothing
        pass

    def log_exception(self, exception: Exception):
        # Stub - does nothing
        pass

    def feature_enabled(self, key: str):
        # Stub - always returns False
        return False

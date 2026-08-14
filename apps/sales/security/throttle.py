from ninja.throttling import SimpleRateThrottle


class IPThrottle(SimpleRateThrottle):
    scope: str

    def __init__(self, rate: str | None = None, scope: str = "ip"):
        super().__init__(rate)
        self.scope = scope

    def get_cache_key(self, request) -> str | None:
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }

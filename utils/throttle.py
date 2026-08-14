from ninja_extra.throttling import DynamicRateThrottle


class DynamicRateThrottleAdvacend(DynamicRateThrottle):

    def get_cache_key(self, request):
        auth_user = getattr(request, "auth", None) # using request.auth instead of request.user

        if auth_user is not None:
            ident = str(getattr(auth_user, "pk", None) or auth_user)
        else:
            ident = self.get_ident(request)  # fallback pro IP

        return self.cache_format % {"scope": self.scope, "ident": ident}
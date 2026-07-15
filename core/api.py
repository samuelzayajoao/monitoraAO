from ninja_extra import NinjaExtraAPI
from apps.auths.controllers import controllers

api = NinjaExtraAPI(
    title="MonitoraAO",
    description="API monitoring transactions.",
    version="1.0.0",
    urls_namespace="api-v1",
)


api.register_controllers(*controllers)

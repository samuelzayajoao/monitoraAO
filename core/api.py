from ninja_extra import NinjaExtraAPI
from apps.auths.controllers import AuthController, CustomJWTController
from apps.projects.controllers import (
    ProjectController,
    IntegrationController,
    CollaboratorController,
)
from apps.sales.routes import SalesController

api = NinjaExtraAPI(
    title="MonitoraAO",
    description="API monitoring transactions.",
    version="1.0.0",
    urls_namespace="api-v1",
)


api.register_controllers(*(AuthController, CustomJWTController))

api.register_controllers(
    *(ProjectController, IntegrationController, CollaboratorController)
)

api.register_controllers(*(SalesController,))

from ninja import ModelSchema
from ..models import ProjectAPIKey

class ProjectAPIKeyOut(ModelSchema):

    class Meta:
        model = ProjectAPIKey
        fields = ["api_key", "project", "expired_at"]
    
    
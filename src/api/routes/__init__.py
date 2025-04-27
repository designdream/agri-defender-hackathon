# Import all routers to make them available from the routes package
from src.api.routes.sensors import router as sensors_router
from src.api.routes.threats import router as threats_router
from src.api.routes.analytics import router as analytics_router
from src.api.routes.admin import router as admin_router

# Export all routers
__all__ = ['sensors', 'threats', 'analytics', 'admin']


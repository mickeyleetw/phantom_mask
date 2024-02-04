import newrelic.agent
import sentry_sdk
import sqlalchemy.orm
from asgi_correlation_id import CorrelationIdMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from apps.pharmacy import pharmacy
from apps.user import user
from apps.purchase_record import purchase_record
from apps.mask import mask
from core.fastapi import FastAPI
from core.handler import add_exception_handlers
from settings import APP_IMAGE_VERSION, APP_URL_VERSION

sqlalchemy.orm.configure_mappers()

app = FastAPI(
    title='Phantom Mask API',
    version=APP_IMAGE_VERSION,
)
add_exception_handlers(app)
app.include_router(pharmacy.router)
app.include_router(user.router)
app.include_router(mask.router)
app.include_router(purchase_record.router)

app.add_versioning(APP_URL_VERSION)


@app.get('/', include_in_schema=False)
async def root():
    return {'status': 0}

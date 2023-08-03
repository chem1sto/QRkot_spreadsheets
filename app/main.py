from fastapi import FastAPI
import uvicorn

from app.api.routers import main_router
from app.core import create_first_superuser, settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description
)

app.include_router(main_router)


@app.on_event('startup')
async def startup():
    await create_first_superuser()


if __name__ == '__main__':
    uvicorn.run('app.main:app', reload=True)

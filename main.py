from fastapi import FastAPI

import uvicorn
from scr.users.views import router as users_router
from healthcheck.views import router as healthcheck_router

from scr.auth.views import router


app = FastAPI()

app.include_router(users_router)
app.include_router(router=healthcheck_router)
app.include_router(router=router)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=5000, host="0.0.0.0")

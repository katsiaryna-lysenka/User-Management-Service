from fastapi import APIRouter, FastAPI, HTTPException

router = APIRouter(tags=["Healthcheck"])

app = FastAPI()


@router.get("/healthcheck/")
async def healthcheck():
    is_server_running_properly = True

    if not is_server_running_properly:
        raise HTTPException(status_code=503, detail="Server is not working properly")

    return {"status": "ok"}

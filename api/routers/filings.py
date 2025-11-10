from fastapi import APIRouter, Depends, Response
from auth import verify_token
from services.filings_service import download_filings
from models import APIResponse

router = APIRouter()

@router.get("/filings", response_model=APIResponse)
def get_filings(tick: str, inter: str = "quarterly", response: Response = None, _: bool = Depends(verify_token)):
    if inter not in ["quarterly", "yearly"]:
        response.status_code = 400
        return APIResponse(status=400, response={"error": "Invalid interval. Use 'quarterly' or 'yearly'"})

    try:
        result = download_filings(tick, inter)
        response.status_code = 200
        return APIResponse(status=200, response=result)
    except Exception as e:
        response.status_code = 500
        return APIResponse(status=500, response={"error": str(e)})

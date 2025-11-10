from fastapi import APIRouter, Depends, Response
from auth import verify_token
from services.data_loader import get_dataframe
from models import APIResponse

router = APIRouter()

@router.get("/search_listed", response_model=APIResponse)
def search_listed(query: str, etf: bool = False, response: Response = None, _: bool = Depends(verify_token)):
    df = get_dataframe()
    query_lower = query.lower()

    results = df[
        df['symbol_lower'].str.contains(query_lower, na=False) |
        df['name_lower'].str.contains(query_lower, na=False)
    ].copy()

    if not etf:
        results = results[results['ETF'] == 'N']

    results['exact_match'] = results['symbol_lower'] == query_lower
    results = results.sort_values(['exact_match', 'symbol'], ascending=[False, True])

    data = results[['symbol', 'name']].to_dict('records')
    response.status_code = 200

    return APIResponse(status=200, response=data)

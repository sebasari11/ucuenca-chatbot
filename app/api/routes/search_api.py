# from fastapi import APIRouter
# from app.schemas.search import SearchRequest, SearchResponse
# from app.services.search_service import perform_search

# router = APIRouter(prefix="/search", tags=["Search"])


# @router.post("/", response_model=SearchResponse)
# def search(request: SearchRequest):
#     return perform_search(request)


# # @router.post("/smart_search", response_model=SearchSmartResponse)
# # def search(request: SearchRequest):
# #     return perform_smart_search(request)

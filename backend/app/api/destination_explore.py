from fastapi import APIRouter, HTTPException, status
import logging

from app.models.destination_explore import (
    DestinationExploreRequest,
    DestinationExploreResponse,
)
from app.services.destination_explore_service import get_destination_explore_service


router = APIRouter(tags=["Destination Intelligence"])
logger = logging.getLogger(__name__)


@router.post(
    "/destination/explore",
    response_model=DestinationExploreResponse,
    status_code=status.HTTP_200_OK,
    summary="Explore a state with AI-powered destination intelligence",
    description="Returns major tourist places in an Indian state with concise historical, architectural, and cultural insights.",
)
async def explore_destination(payload: DestinationExploreRequest):
    try:
        service = get_destination_explore_service()
        result = await service.explore_state(
            state=payload.state,
            include_google_places=payload.include_google_places,
            force_refresh=payload.force_refresh,
        )
        return DestinationExploreResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("[Destination Explore] Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate destination intelligence. Please try again.",
        )

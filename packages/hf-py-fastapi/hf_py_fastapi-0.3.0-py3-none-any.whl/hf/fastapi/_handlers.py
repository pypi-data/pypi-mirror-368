from fastapi import Response, status


async def health_handler() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)

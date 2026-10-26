
from httpx import AsyncClient


async def test_process_time_header_exists(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    assert "x-process-time" in response.headers

    process_time = float(response.headers["x-process-time"])
    assert process_time >= 0

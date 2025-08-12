import pytest

from ey_commerce_lib.kogan.main import KoganClient
from ey_commerce_lib.kogan.schemas.query.product import KoganProductQuery


@pytest.mark.asyncio
async def test_client():
    async with KoganClient(
        seller_id="xxx",
        seller_token="xxxx"
    ) as client:
        print(await client.products(
            KoganProductQuery(search="Boys Michael Jackson Cosplay Costume Black Suit Set Fancy MJ Outfit (Size:120)")))

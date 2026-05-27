import asyncio
import aiohttp

async def send_requests(url, n_requests=100_000, concurrency=150):
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        async def bound_request():
            async with sem:
                try:
                    async with session.post(url, json={
                        "user_id": 1, "product_id": 42, "purchased_count": 1
                    }) as resp:
                        return resp.status
                except Exception as e:
                    return str(e)

        tasks = [bound_request() for _ in range(n_requests)]
        results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    results = asyncio.run(send_requests("http://localhost:8000/purchase"))
    print(f"Успешных (200): {results.count(200)}")
    print(f"Ошибок: {len(results) - results.count(200)}")
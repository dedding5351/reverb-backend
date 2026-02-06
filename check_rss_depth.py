import asyncio
import httpx
import xml.etree.ElementTree as ET

async def check_rss_pagination():
    base_url = "https://airbnb.tech/feed/"
    # Common wordpress RSS pagination patterns
    urls_to_test = [
        "https://airbnb.tech/feed/",
        "https://airbnb.tech/feed/?paged=2",
        "https://airbnb.tech/feed/page/2/"
    ]
    
    async with httpx.AsyncClient() as client:
        for url in urls_to_test:
            print(f"Fetching {url}...")
            response = await client.get(url, follow_redirects=True)
            try:
                root = ET.fromstring(response.text)
                channel = root.find("channel")
                items = channel.findall("item") if channel else []
                print(f" - Status: {response.status_code}")
                print(f" - Item count: {len(items)}")
                if items:
                    print(f" - First item: {items[0].find('title').text}")
                    print(f" - Last item: {items[-1].find('title').text}")
            except Exception as e:
                print(f" - Failed to parse: {e}")

if __name__ == "__main__":
    asyncio.run(check_rss_pagination())

"""Plugin API client."""

from typing import List, Optional

from pydantic import BaseModel

from .common import get_api_client


class Category(BaseModel):
    """Plugin category information."""

    name: str
    slug: str
    description: str


class Plugin(BaseModel):
    """Plugin information."""

    slug: str
    url: str
    repository_name: str
    repository_owner: str
    repository_description: Optional[str] = None
    categories: Optional[List[Category]] = None


class SearchResponse(BaseModel):
    """Search response wrapper."""

    plugins: List[Plugin] = []


class PluginsAPI:
    """Plugin repository API client."""

    async def get_categories(self) -> List[Category]:
        """Get all plugin categories."""
        client = await get_api_client()
        data = await client.get_json("/plugin-repository/search/categories", auth=False)
        return [Category(name=item["name"], slug=item["slug"], description=item["description"]) for item in data]

    async def get_plugins(self, limit: int = 20, offset: int = 0) -> SearchResponse:
        """Get all plugins with pagination."""
        client = await get_api_client()
        data = await client.get_json(f"/plugin-repository/search?limit={limit}&offset={offset}", auth=False)
        plugins_list = []
        for hit in data.get("plugins", {}).get("hits", []):
            categories = []
            for cat in hit.get("categories", []):
                categories.append(Category(name=cat["name"], slug=cat["slug"], description=cat["description"]))

            metadata = hit.get("metadata", {})
            plugin = Plugin(
                slug=hit["slug"],
                url=hit["url"],
                repository_name=metadata.get("repository_name", ""),
                repository_owner=metadata.get("repository_owner", ""),
                repository_description=metadata.get("repository_description"),
                categories=categories,
            )
            plugins_list.append(plugin)
        return SearchResponse(plugins=plugins_list)

    async def get_plugin(self, slug: str) -> Optional[Plugin]:
        """Get a single plugin by slug."""
        client = await get_api_client()
        data = await client.get_json(f"/plugin-repository/search/plugins/{slug}", auth=False)
        hits = data.get("hits", [])
        if not hits:
            return None

        hit = hits[0]
        categories = []
        for cat in hit.get("categories", []):
            categories.append(Category(name=cat["name"], slug=cat["slug"], description=cat["description"]))

        metadata = hit.get("metadata", {})
        return Plugin(
            slug=hit["slug"],
            url=hit["url"],
            repository_name=metadata.get("repository_name", ""),
            repository_owner=metadata.get("repository_owner", ""),
            repository_description=metadata.get("repository_description"),
            categories=categories,
        )

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> SearchResponse:
        """Search for plugins."""
        client = await get_api_client()
        data = await client.get_json(f"/plugin-repository/search?q={query}&limit={limit}&offset={offset}", auth=False)
        plugins_list = []

        plugins_data = data.get("plugins", {})
        hits = plugins_data.get("hits", [])

        for hit in hits:
            categories = []
            for cat in hit.get("categories", []):
                categories.append(Category(name=cat["name"], slug=cat["slug"], description=cat["description"]))

            metadata = hit.get("metadata", {})
            plugin = Plugin(
                slug=hit["slug"],
                url=hit["url"],
                repository_name=metadata.get("repository_name", ""),
                repository_owner=metadata.get("repository_owner", ""),
                repository_description=metadata.get("repository_description"),
                categories=categories,
            )
            plugins_list.append(plugin)
        return SearchResponse(plugins=plugins_list)


# Global instance
plugins = PluginsAPI()

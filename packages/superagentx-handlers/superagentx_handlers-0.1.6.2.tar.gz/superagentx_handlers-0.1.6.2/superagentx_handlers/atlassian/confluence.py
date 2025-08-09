import logging
import os

import aiohttp
from aiohttp import BasicAuth
from atlassian import Confluence
from superagentx.handler.base import BaseHandler
from superagentx.handler.decorators import tool
from superagentx.utils.helper import sync_to_async

from superagentx_handlers.atlassian.exceptions import AuthException

logger = logging.getLogger(__name__)


class ConfluenceHandler(BaseHandler):
    """
        A handler class for managing interactions with the Jira API.
        This class extends BaseHandler and provides methods for performing various Jira operations,
        such as creating, updating, retrieving, and managing issues and projects within a Jira environment.
    """

    def __init__(
            self,
            *,
            email: str | None = None,
            token: str | None = None,
            organization: str | None = None
    ):
        super().__init__()
        self.email = email or os.getenv('ATLASSIAN_EMAIL')
        self.token = token or os.getenv('ATLASSIAN_TOKEN')
        self.organization = organization or os.getenv('ATLASSIAN_ORGANIZATION')
        self._connection: Confluence = self._connect()

    def _connect(self) -> Confluence:
        try:
            confluence = Confluence(
                url=f'https://{self.organization}.atlassian.net',
                token=self.token
            )
            logger.info("Confluence Authenticate Success")
            return confluence
        except Exception as ex:
            message = f'Confluence Handler Authentication Problem {ex}'
            logger.error(message, exc_info=ex)
            raise AuthException(message)

    @tool
    async def get_all_spaces(
            self,
            *,
            start: int = 0,
            limit: int = 25,
    ):
        try:
            result = await sync_to_async(
                self._connection.get_all_spaces,
                start=start,
                limit=limit,
            )
            spaces_url = result["_links"]["self"]
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        spaces_url,
                        auth=BasicAuth(self.email, self.token),
                        headers={'Content-Type': 'application/json'}
                ) as resp:
                    return await resp.json()
        except Exception as ex:
            message = f"Error While getting confluence spaces! {ex}"
            logger.error(message, exc_info={ex})
            raise Exception(message)

    @tool
    async def get_pages_spaces(
            self,
            *,
            space_key: str,
            start: int = 0,
            limit: int = 25,
    ):
        try:
            return await sync_to_async(
                self._connection.get_all_pages_from_space,
                space=space_key,
                expand="children.page",
                start=start,
                limit=limit
            )
        except Exception as ex:
            message = f"Error While getting confluence spaces! {ex}"
            logger.error(message, exc_info={ex})
            raise Exception(message)

    @tool
    async def last_updated_pages(
            self,
            *,
            space_key: str,
            title: str,
            start: int = 0,
            limit: int = 1
    ) -> dict:
        try:
            result = await sync_to_async(
                self._connection.get_page_by_title,
                space=space_key,
                title=title,
                start=start,
                limit=limit,
                expand='title,history.lastUpdated',
                type="page"
            )
            return result['history'] if result else None
        except Exception as ex:
            message = f"Error While getting last updated info! {ex}"
            logger.error(message, exc_info={ex})
            raise Exception(message)

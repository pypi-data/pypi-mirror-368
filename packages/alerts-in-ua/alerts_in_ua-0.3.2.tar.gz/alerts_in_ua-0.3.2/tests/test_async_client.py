import asyncio
import unittest
from unittest.mock import MagicMock, patch

from alerts_in_ua.async_client import AsyncClient
from alerts_in_ua.errors import UnauthorizedError, ForbiddenError, RateLimitError, InternalServerError, ApiError

class TestAsyncClient(unittest.TestCase):
    def setUp(self):
        self.client = AsyncClient("a736816935feb867fe05d69df973f0f4a1b0f20d9d77a8c")

    @patch("aiohttp.ClientSession.get")
    async def test_get_active_alerts(self, mock_get):
        # Test successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Last-Modified": "Tue, 24 Feb 2022 01:40:00 GMT"}
        mock_response.json = MagicMock(return_value={})
        mock_get.return_value = mock_response

        data = await self.client.get_active_alerts()
        self.assertIsNotNone(data)

        # Test Unauthorized error
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.json = MagicMock(return_value={"message": "Unauthorized: Incorrect token"})
        mock_get.return_value = mock_response

        with self.assertRaises(UnauthorizedError):
            await self.client.get_active_alerts()

        # Test Forbidden error
        mock_response = MagicMock()
        mock_response.status = 403
        mock_response.json = MagicMock(return_value={"message": "Forbidden. API may not be available in some regions. Please ask api@alerts.in.ua for details."})
        mock_get.return_value = mock_response

        with self.assertRaises(UnauthorizedError):
            await self.client.get_active_alerts()

        # Test Rate Limit error
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = MagicMock(return_value={"message": "Too many requests: Rate limit exceeded"})
        mock_get.return_value = mock_response

        with self.assertRaises(RateLimitError):
            await self.client.get_active_alerts()

        # Test Internal Server error
        mock_response = MagicMock()
        mock_response.status = 500
        mock_get.return_value = mock_response

        with self.assertRaises(InternalServerError):
            await self.client.get_active_alerts()

        # Test Unknown error
        mock_response = MagicMock()
        mock_response.status = 999
        mock_get.return_value = mock_response

        with self.assertRaises(ApiError):
            await self.client.get_active_alerts()

if __name__ == "__main__":
    asyncio.run(unittest.main())
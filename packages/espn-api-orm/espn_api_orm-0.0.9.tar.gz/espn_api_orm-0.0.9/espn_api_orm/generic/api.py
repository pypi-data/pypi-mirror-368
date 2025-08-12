import time
from enum import Enum
import requests
from espn_api_orm.generic.schema import BaseType


class ESPNBaseAPI:
    """
    ESPNBaseAPI class for making API requests to ESPN's sports data endpoints.

    Attributes:
        _base_url (str): The base URL for ESPN's public API.
        _core_url (str): The base URL for ESPN's core API.

    Methods:
        api_request(url: str, retry_count: int = 0) -> dict or None:
            Makes an API request to the specified URL.

            Args:
                url (str): The complete URL for the API request.
                retry_count (int): The number of times to retry the request in case of failure. Default is 0.

            Returns:
                dict or None: The JSON response from the API, or None if the request was unsuccessful.
                If the response indicates a 404 status code or an error, None is returned.

            Raises:
                Exception: Raises an exception if the request encounters an error after multiple retries.
                This is typically used when the request limit is exceeded (error code 2502).
    """

    def __init__(self):
        """
        Initializes an instance of the ESPNBaseAPI class.

        Attributes:
            _base_url (str): The base URL for ESPN's public API.
            _core_url (str): The base URL for ESPN's core API.
        """
        self._base_url = 'https://site.api.espn.com/apis/site/v2/sports'
        self._core_url = 'https://sports.core.api.espn.com/v2/sports'
        self._common_url = 'https://site.web.api.espn.com/apis/common/v3/sports'

    def get_value(self, url, val):
        return val.ref.replace(f"{url.replace('https', 'http')}/", '').split('?')[0]

    def _get_values(self, url, items):
        return [self.get_value(url, val) for val in items]

    def get_values(self, url, values_url = None):
        if values_url is None:
            values_url = url.split('?')[0]
        values = []
        res = self.api_request(url)
        if res is None:
            return None
        res = BaseType(**res)
        values.extend(list(map(int,self._get_values(values_url, res.items))))
        if res.pageCount > 1:
            for page in range(2,res.pageCount+1):
                res = self.api_request(url+f'&page={page}')
                if res is None:
                    return None
                res = BaseType(**res)
                values.extend(list(map(int,self._get_values(values_url, res.items))))
        return values

    def api_request(self, url: str, retry_count: int = 0):
        """
        Makes an API request to the specified URL.

        Args:
            url (str): The complete URL for the API request.
            retry_count (int): The number of times to retry the request in case of failure. Default is 0.

        Returns:
            dict or None: The JSON response from the API, or None if the request was unsuccessful.
            If the response indicates a 404 status code or an error, None is returned.

        Raises:
            Exception: Raises an exception if the request encounters an error after multiple retries.
            This is typically used when the request limit is exceeded (error code 2502).
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            resp = requests.get(url=url, headers=headers)

            if resp.status_code == 404:
                return None
            res = resp.json()
            if 'error' in res:
                if res['error']['code'] == 404:  # No data
                    return None
                if res['error']['code'] == 500:  # 500 Error
                    return None
            if 'code' in res:
                if res['code'] == 2502:
                    raise Exception('Flooded')  # Too many requests
                if res['code'] == 400:  # Data cant be found (wrong endpoint/wrong request)
                    return None

            return res
        except Exception as e:
            if retry_count >= 3:
                raise e
            time.sleep(5)
            print(f'URL error for {url}')
            self.api_request(url, retry_count=retry_count + 1)

    def get_sports(self, return_values=True):
        """
        Retrieves sports data from the API.

        Parameters:
            return_values (bool): Whether to return the values of the sports data. Default is True.

        Returns:
            If `return_values` is True, returns a list of values from the sports data.
            If `return_values` is False, returns a `BaseType` object representing the sports data.
        """
        res = BaseType(**self.api_request(f"{self._core_url}"))
        if not return_values:
            return res
        return self._get_values(f"{self._core_url}", res.items)

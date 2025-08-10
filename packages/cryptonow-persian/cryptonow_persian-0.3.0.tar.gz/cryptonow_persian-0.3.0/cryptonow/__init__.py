"""
cryptonow - Advanced crypto price getter with async support, caching, Persian names, and more.
"""
import time
import httpx

class CryptoNow:
    def __init__(self):
        self.cache = {}
        self.last_fetch = {}
        self.cache_ttl = 60  # seconds
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"
        self.use_fallback = False
        self.format_irr = False

        # نام‌ها و نمادها
        self.mapping = {
            # انگلیسی
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'doge': 'dogecoin',
            'dogecoin': 'dogecoin',
            'bnb': 'binancecoin',
            'cardano': 'cardano',
            'ada': 'cardano',
            # فارسی
            'بیت‌کوین': 'bitcoin',
            'اتریوم': 'ethereum',
            'دوج': 'dogecoin',
            'بایننس': 'binancecoin',
            # اختصاری فارسی
            'ب.ک': 'bitcoin',
            'ا.م': 'ethereum',
            'د.ک': 'dogecoin',
        }

    def _should_update(self, coin_id):
        return time.time() - self.last_fetch.get(coin_id, 0) > self.cache_ttl

    async def async_get(self, key, currency='usd'):
        """دریافت قیمت به صورت async"""
        coin_id = self._get_coin_id(key)
        currency = currency.lower()
        if self._should_update(coin_id):
            await self._async_fetch(coin_id, currency)
        return self._format_price(coin_id, currency)

    def __getitem__(self, key):
        """دریافت قیمت به صورت sync"""
        if isinstance(key, tuple):
            coin_name, currency = key
        else:
            coin_name, currency = key, 'usd'

        coin_id = self._get_coin_id(coin_name)
        currency = currency.lower()

        if self._should_update(coin_id):
            self._fetch(coin_id, currency)

        return self._format_price(coin_id, currency)

    def _get_coin_id(self, name):
        name = str(name).lower().strip()
        if name not in self.mapping:
            raise KeyError(f"Unknown coin: {name}")
        return self.mapping[name]

    def _fetch(self, coin_id, currency):
        try:
            params = {
                "ids": coin_id,
                "vs_currencies": currency,
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            response = httpx.get(self.base_url, params=params, timeout=10)
            data = response.json()
            self.cache[coin_id] = data[coin_id]
            self.last_fetch[coin_id] = time.time()
        except:
            if coin_id not in self.cache:
                raise ConnectionError("Failed to fetch price")

    async def _async_fetch(self, coin_id, currency):
        try:
            params = {
                "ids": coin_id,
                "vs_currencies": currency,
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10)
                data = response.json()
                self.cache[coin_id] = data[coin_id]
                self.last_fetch[coin_id] = time.time()
        except:
            if coin_id not in self.cache:
                raise ConnectionError("Failed to fetch price")

    def _format_price(self, coin_id, currency):
        price = self.cache[coin_id][currency]
        if currency == 'irr' and self.format_irr:
            # قالب‌بندی فارسی
            return f"{price:,.0f}".replace(',', '٬') + " تومان"
        return price

    @property
    def info(self):
        class InfoMode:
            def __getitem__(_, key):
                if isinstance(key, tuple):
                    coin_name, currency = key
                else:
                    coin_name, currency = key, 'usd'
                
                price = NOW[coin_name, currency]
                coin_id = NOW._get_coin_id(coin_name)
                data = NOW.cache.get(coin_id, {})
                
                return {
                    'price': price,
                    'change_24h': data.get(f'{currency}_24h_change'),
                    'volume': data.get(f'{currency}_24h_vol'),
                    'currency': currency.upper()
                }
        return InfoMode()

    @property
    def cached(self):
        class CachedMode:
            def __getitem__(_, key):
                if isinstance(key, tuple):
                    coin_name, currency = key
                else:
                    coin_name, currency = key, 'usd'
                coin_id = NOW._get_coin_id(coin_name)
                if coin_id in NOW.cache:
                    return NOW._format_price(coin_id, currency)
                raise KeyError("Not in cache")
        return CachedMode()

    @property
    def online(self):
        class OnlineMode:
            def __getitem__(_, key):
                if isinstance(key, tuple):
                    coin_name, currency = key
                else:
                    coin_name, currency = key, 'usd'
                coin_id = NOW._get_coin_id(coin_name)
                NOW._fetch(coin_id, currency)
                return NOW._format_price(coin_id, currency)
        return OnlineMode()

# نمونه‌سازی اصلی
NOW = CryptoNow()

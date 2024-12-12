import os

import aiohttp
from config import PROFIT_MARGIN, EXCHANGE_API_KEY


class CurrencyConverter:
    def __init__(self):
        self.base_url = "https://api.nobitex.ir/market/stats"  # یا هر API دیگری که ترجیح می‌دهید
        self.cache_timeout = 300  # به‌روزرسانی هر 5 دقیقه
        self._cached_rates = None
        self._last_update = 0

    async def get_eur_to_irr_rate(self) -> float:
        """دریافت نرخ تبدیل یورو به ریال"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    data = await response.json()
                    # این مقادیر بسته به API مورد استفاده متفاوت خواهد بود
                    usd_to_irr = float(data['stats']['USDIRT']['latest'])
                    eur_to_usd = 1.08  # این مقدار باید از API مناسب گرفته شود
                    return usd_to_irr * eur_to_usd
        except Exception as e:
            return os.getenv("USD_TO_IR") * 1.08  # مقدار پیش‌فرض

    def calculate_final_price(self, eur_price: float) -> dict:
        """محاسبه قیمت نهایی با احتساب سود و کارمزدها"""
        # افزودن حاشیه سود
        price_with_margin = eur_price * PROFIT_MARGIN

        # کارمزدهای ثابت (به یورو)
        FIXED_FEES = {
            'maintenance': 2,  # هزینه نگهداری
            'payment_gateway': 1,  # کارمزد درگاه پرداخت
            'support': 3,  # هزینه پشتیبانی
        }

        total_eur = price_with_margin + sum(FIXED_FEES.values())

        return {
            'original_eur': eur_price,
            'with_margin_eur': price_with_margin,
            'fees_eur': FIXED_FEES,
            'total_eur': total_eur,
            'fees_breakdown': FIXED_FEES
        }


currency_converter = CurrencyConverter()

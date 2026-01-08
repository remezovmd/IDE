import requests
from lxml import etree
from config import valute_dict


class ConversionException(Exception):
    pass


class ValuteConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        """Takes currency quotes from the API http://www.cbr.ru/scripts/XML_daily.asp 
        and calculates the cost for the specified amount
        Args:
            base (str): base currency
            quote (str): quote currency
            amount (str): amount
        Returns:
            float
        """
        base_price = 0
        quote_price = 0
        
        if base not in valute_dict.keys():
            raise ConversionException(f'Не удалось обработать валюту {base}')
        if quote not in valute_dict.keys():
            raise ConversionException(f'Не удалось обработать валюту {quote}')
    
        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise ConversionException(f'Не удалось обработать количество {amount}')
    
        r = requests.get('http://www.cbr.ru/scripts/XML_daily.asp').content
        root = etree.fromstring(r)
        
        for valute in root.getchildren():
            for elem in valute.getchildren():
                if valute_dict[quote] == 'RUR':
                    quote_price = 1
                if valute_dict[base] == 'RUR':
                    base_price = 1
                if elem.text == valute_dict[quote]:
                    quote_price = float(valute.getchildren()[4].text.replace(',', '.'))
                if elem.text == valute_dict[base]:
                    base_price = float(valute.getchildren()[4].text.replace(',', '.'))      
        if base_price and quote_price: 
            return round(base_price / quote_price * amount, 4)
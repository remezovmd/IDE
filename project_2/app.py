import telebot
from config import TOKEN, valute_dict
from extensions import ConversionException, ValuteConverter

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    """Show instructions for the start and help commands
    Args:
        message (str): message object from TG
    Returns:
        None
    """
    text = 'Чтобы начать работу введите комманду боту в следующем формате:\n<имя валюты> <в какую валюту перенести> \
<количество переводимой валюты>\nНапример:\nрубль доллар 100\nУвидеть список всех доступных валют: /values'
    bot.reply_to(message, text)

@bot.message_handler(commands=['values',])
def handle_values(message):
    """Show list of currencies
    Args:
        message (str): message object from TG
    Returns:
        None
    """
    text = 'Доступные валюты:'
    for key in valute_dict.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    """Convert currencies from message text and send result to TG
    Args:
        message (str): message object from TG
    Returns:
        None
    """
    try:
        args = message.text.split()
        if len(args) != 3:
            raise ConversionException('Неверный формат запроса')
        base, quote, amount = args
        price = ValuteConverter.get_price(base, quote, amount)
    except ConversionException as e:
        bot.reply_to(message, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду.\n{e}')
    else:
        bot.send_message(message.chat.id, f'Цена {amount} {base} в {quote} - {price}')
    
bot.polling(none_stop=True)
# my-nalog

Python клиент для API "Мой Налог" (lknpd.nalog.ru)

## Установка

```bash
pip install my-nalog
```

## Использование

```python
from my_nalog import NalogRuAPI

api = NalogRuAPI()

# Авторизация по SMS
sms_response = api.request_sms_code("79991234567")
api.verify_sms_code("123456", sms_response['challengeToken'])

# Создание чека
receipt = api.create_receipt(100.50, "Тестовая услуга")
print(receipt['approvedReceiptUuid'])
```

## Лицензия

MIT
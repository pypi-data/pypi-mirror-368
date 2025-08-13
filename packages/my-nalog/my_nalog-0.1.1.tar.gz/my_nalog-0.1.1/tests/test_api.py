from my_nalog import NalogRuAPI, AuthError, ReceiptError

def main():
    api = NalogRuAPI()
    
    try:
        if not api.is_authenticated():
            print("Выберите способ авторизации:")
            print("1. По SMS")
            print("2. По ИНН и паролю")
            choice = input("Ваш выбор (1/2): ")
            
            if choice == "1":
                phone = input("Введите номер телефона (11 цифр): ")
                api.auth_by_sms(phone)
                code = input("Введите код из SMS: ")
                profile = api.verify_sms(code, api.last_challenge_token)
            elif choice == "2":
                inn = input("Введите ИНН: ")
                password = input("Введите пароль: ")
                profile = api.auth_by_password(inn, password)
            else:
                print("Неверный выбор")
                return
                
            print(f"Авторизация успешна! ИНН: {profile.inn}")
        
        # Создание чека
        amount = float(input("Введите сумму чека: "))
        description = input("Введите описание услуги: ")
        
        receipt = api.create_receipt(amount, description)
        print(f"Чек создан! Ссылка: {receipt.link}")
        
    except AuthError as e:
        print(f"Ошибка авторизации: {str(e)}")
    except ReceiptError as e:
        print(f"Ошибка создания чека: {str(e)}")
    except Exception as e:
        print(f"Неизвестная ошибка: {str(e)}")

if __name__ == "__main__":
    main()
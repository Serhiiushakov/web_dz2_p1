import datetime
import pickle


# Базовий клас для зберігання значення поля
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Клас для зберігання імені контакту
class Name(Field):
    def __init__(self, value):
        super().__init__(value)


# Клас для зберігання номера телефону з валідацією формату (10 Знаків)
class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate_phone(value):
            raise ValueError("Incorrect phone number format")

    def validate_phone(self, phone):
        return len(phone) == 10 and phone.isdigit()


# Клас для зберігання дати народження з валідацією формату (дд.мм.рррр)
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Додати номер телефону до контакту
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    # Видалити номер телефону з контакту
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    # Редагувати існуючий номер телефону
    def edit_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if str(phone) == old_phone:
                self.phones[idx] = Phone(new_phone)
                break

    # Знайти номер телефону в контакті
    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    # Додати дату народження до контакту
    def add_birthday(self, birthday):
        if self.birthday is None:
            self.birthday = Birthday(birthday)
        else:
            raise ValueError("Birthday is already set for this record.")

    def __str__(self):
        return f"Contact: {self.name.value}, phone: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"


# Клас для зберігання адресної книги
class AddressBook:
    def __init__(self):
        self.contacts = {}

    # Додати контакт до адресної книги
    def add_contact(self, name, phone):
        if name in self.contacts:
            self.contacts[name].add_phone(phone)
        else:
            self.contacts[name] = Record(name)
            self.contacts[name].add_phone(phone)

    # Змінити контакт у адресній книзі
    def change_contact(self, name, phone):
        if name in self.contacts:
            self.contacts[name].add_phone(phone)
        else:
            raise KeyError("Contact not found.")

    # Показати номер телефону для заданого контакту
    def show_phone(self, name):
        if name in self.contacts:
            return f"The phone number for {name} is {'; '.join(str(p) for p in self.contacts[name].phones)}"
        else:
            raise KeyError("Contact not found.")

    # Показати всі контакти у адресній книзі
    def show_all(self):
        if self.contacts:
            return "\n".join([str(record) for record in self.contacts.values()])
        else:
            raise ValueError("No contacts found.")

    # Додати дату народження до контакту
    def add_birthday(self, name, birthday):
        if name in self.contacts:
            self.contacts[name].add_birthday(birthday)
        else:
            raise KeyError("Contact not found.")

    # Показати дату народження для заданого контакту
    def show_birthday(self, name):
        if name in self.contacts:
            return self.contacts[name].birthday
        else:
            raise KeyError("Contact not found.")

    # Показати дні народження на наступний тиждень, включаючи перенесення з вихідних на понеділок
    # (Суботу та неділю переносимо на понеділок)
    def birthdays(self):
        today = datetime.date.today()
        upcoming_birthdays = {}
        for i in range(7):
            day = today + datetime.timedelta(days=i)
            weekday = day.weekday()
            if weekday in (5, 6):  # Субота (5) або неділя (6)
                next_monday = day + datetime.timedelta(days=(7 - weekday))
                upcoming_birthdays[next_monday] = upcoming_birthdays.get(next_monday, [])
            else:
                upcoming_birthdays[day] = upcoming_birthdays.get(day, [])

        for name, record in self.contacts.items():
            if record.birthday is not None:
                bday_this_year = record.birthday.value.replace(year=today.year)
                if today <= bday_this_year <= today + datetime.timedelta(days=6):
                    weekday = bday_this_year.weekday()
                    if weekday in (5, 6):
                        next_monday = bday_this_year + datetime.timedelta(days=(7 - weekday))
                        upcoming_birthdays[next_monday].append(name)
                    else:
                        upcoming_birthdays[bday_this_year].append(name)

        return {k: v for k, v in sorted(upcoming_birthdays.items()) if v}


# 22/05/2024# Функція для збереження даних адресної книги у файл
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


# 22/05/2024# Функція для завантаження даних адресної книги з файлу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


# Декоратор для обробки помилок введення користувача
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:  ## Перероблена обробка ValueError для показу конкретної помилки
            return f"{e}"
        except KeyError as e:
            return f"Invalid command. {str(e)}"
        except IndexError:
            return "Invalid command. Usage: command username phone"
        except Exception as e:  ## Перероблена обробка загальних помилок для показу конкретної помилки
            return f"An error occurred: {str(e)}"

    return inner


# Розбирає введений користувачем рядок на команду та аргументи
def parse_input(user_input):
    if not user_input:  ## Обробка пустого вводу комади в боті
        return None, []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError("Invalid command. Usage: add username phone")
    name, phone = args
    book.add_contact(name, phone)
    return "Contact added."


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError("Invalid command. Usage: change username phone")
    name, phone = args
    book.change_contact(name, phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError("Invalid command. Usage: phone username")
    name = args[0]
    return book.show_phone(name)


@input_error
def show_all(book: AddressBook):
    return book.show_all()


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise IndexError("Invalid command. Usage: add-birthday username DD.MM.YYYY")
    name, birthday = args
    book.add_birthday(name, birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError("Invalid command. Usage: show-birthday username")
    name = args[0]
    birthday = book.show_birthday(name)
    return f"{name}'s birthday is on {birthday}."


@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays next week."
    result = []
    for date, names in upcoming_birthdays.items():
        result.append(f"{date.strftime('%A %d.%m.%Y')}: {', '.join(names)}")
    return "Upcoming birthdays:\n" + "\n".join(result)


# Головна функція для обробки команд користувача
def main():
    # 22/05/2024# Завантаження даних адресної книги з файлу при запуску
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # 22/05/2024# Збереження даних адресної книги у файл перед виходом
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        elif command is None:  ## Обробка пустого вводу
            print("Please enter a command.")

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
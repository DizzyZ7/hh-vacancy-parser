import requests
from openpyxl import Workbook
import re


# =========================
# ТВОИ НАВЫКИ (из резюме)
# =========================

MY_SKILLS = {
    "python": 10,
    "sql": 10,
    "linux": 8,
}

def extract_vacancy_id(url: str) -> str:
    part = url.split("/vacancy/")[-1]
    return part.split("?")[0]


def clean_html(raw_html: str) -> str:
    clean = re.compile('<.*?>')
    return re.sub(clean, '', raw_html)


def split_sections(text: str):
    text_lower = text.lower()

    responsibilities = ""
    requirements = ""
    conditions = ""

    patterns = {
        "responsibilities": r"(обязанности.*?)(требования|условия|$)",
        "requirements": r"(требования.*?)(условия|$)",
        "conditions": r"(условия.*)"
    }

    r = re.search(patterns["responsibilities"], text_lower, re.DOTALL)
    if r:
        responsibilities = r.group(1)

    r = re.search(patterns["requirements"], text_lower, re.DOTALL)
    if r:
        requirements = r.group(1)

    r = re.search(patterns["conditions"], text_lower, re.DOTALL)
    if r:
        conditions = r.group(1)

    return responsibilities[:1000], requirements[:1000], conditions[:1000]


def detect_employment_type(text: str):
    text = text.lower()

    if "тк рф" or "трудовой" in text:
        return "ТК РФ"
    if "гпх" in text:
        return "ГПХ"
    if "самозанят" in text:
        return "Самозанятость"
    if "ип" in text:
        return "ИП"
    return "Не указано"


def rate_vacancy(text: str):
    score = 0
    found = []

    text = text.lower()

    for skill, weight in MY_SKILLS.items():
        if skill in text:
            score += weight
            found.append(skill)

    return score, ", ".join(found)


def verdict(score: int):
    if score >= 60:
        return "🟢 Отличное совпадение"
    elif score >= 35:
        return "🟡 Среднее совпадение"
    else:
        return "🔴 Слабое совпадение"


def format_salary(salary_data):
    if not salary_data:
        return "Не указана"

    salary_from = salary_data.get("from")
    salary_to = salary_data.get("to")
    currency = salary_data.get("currency", "")

    if salary_from and salary_to:
        return f"{salary_from}-{salary_to} {currency}"
    elif salary_from:
        return f"от {salary_from} {currency}"
    elif salary_to:
        return f"до {salary_to} {currency}"
    else:
        return "Не указана"


# =========================
# ОСНОВНОЙ ПАРСИНГ
# =========================

def get_vacancy_data(vacancy_id: str):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка получения {vacancy_id}")
        return None

    data = response.json()

    description_raw = data.get("description", "")
    description = clean_html(description_raw)

    responsibilities, requirements, conditions = split_sections(description)

    score, found_skills = rate_vacancy(description)
    employment_type = detect_employment_type(description)

    return {
        "Компания": data["employer"]["name"],
        "Должность": data["name"],
        "Город": data["area"]["name"],
        "Формат работы": ", ".join([f["name"] for f in data.get("work_format", [])]) if data.get("work_format") else "Не указано",
        "Тип занятости": data["employment"]["name"] if data.get("employment") else "Не указано",
        "График": data["schedule"]["name"] if data.get("schedule") else "Не указано",
        "Опыт": data["experience"]["name"] if data.get("experience") else "Не указано",
        "Зарплата": format_salary(data.get("salary")),
        "Тип оформления": employment_type,
        "Обязанности": responsibilities,
        "Требования": requirements,
        "Условия": conditions,
        "Совпадение навыков": found_skills,
        "Рейтинг (0-100)": score,
        "Вердикт": verdict(score),
        "Ссылка": data["alternate_url"]
    }


def save_to_excel(vacancies: list):
    wb = Workbook()
    ws = wb.active
    ws.title = "Vacancies"

    headers = list(vacancies[0].keys())
    ws.append(headers)

    for vacancy in vacancies:
        ws.append(list(vacancy.values()))

    wb.save("parsed_vacancies_PRO.xlsx")
    print("Файл parsed_vacancies_PRO.xlsx создан!")


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    print("Вставляй ссылки hh.ru (по одной).")
    print("Когда закончишь — введи 'стоп'\n")

    vacancies = []

    while True:
        link = input("Ссылка: ")

        if link.lower() == "стоп":
            break

        vacancy_id = extract_vacancy_id(link)
        data = get_vacancy_data(vacancy_id)

        if data:
            vacancies.append(data)
            print(f"Добавлено: {data['Должность']} | {data['Компания']} | {data['Рейтинг (0-100)']}")

    if vacancies:
        save_to_excel(vacancies)
    else:
        print("Нет данных.")

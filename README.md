# HH Vacancy Parser

Парсер вакансий с hh.ru на Python, который:

- Извлекает описание вакансий по ссылке
- Разбивает описание на обязанности, требования и условия
- Определяет тип занятости (ТК РФ, ГПХ, самозанятость, ИП)
- Сравнивает навыки кандидата с требованиями вакансии
- Выставляет рейтинг и вердикт совпадения навыков
- Сохраняет результаты в Excel (`parsed_vacancies_PRO.xlsx`)

## Установка
```bash
git clone https://github.com/yourusername/hh-vacancy-parser.git
cd hh-vacancy-parser
pip install -r requirements.txt

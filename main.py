# Головна програма для БД "Телефонна станція" (Варіант 9)
# Виводить таблиці та виконує SQL запити

import psycopg
from tabulate import tabulate


# Налаштування підключеня до БД
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'dbname': 'phone_station',
    'user': 'admin',
    'password': 'admin123'
}


# Підключеня до БД
def get_connection():
    return psycopg.connect(**DB_CONFIG)


# Виконати запит і повернути результат
def execute_query(cursor, query, params=None):
    cursor.execute(query, params)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


# Вивід таблиці у форматі grid
def print_table(title, columns, rows):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    if rows:
        print(tabulate(rows, headers=columns, tablefmt="grid"))
    else:
        print("Немає даних")
    print()


# Вивід всіх таблиць БД
def display_all_tables(cursor):
    
    # Клієнти
    columns, rows = execute_query(cursor, """
        SELECT client_id AS "Код клієнта", 
               client_type AS "Тип клієнта", 
               address AS "Адреса",
               last_name AS "Прізвище", 
               first_name AS "Ім'я", 
               middle_name AS "По батькові"
        FROM clients
        ORDER BY client_id
    """)
    print_table("ТАБЛИЦЯ: КЛІЄНТИ (clients)", columns, rows)
    
    # Тарифи
    columns, rows = execute_query(cursor, """
        SELECT tariff_id AS "Код тарифу", 
               call_type AS "Тип дзвінка", 
               price_per_minute AS "Вартість за хвилину (грн)"
        FROM tariffs
        ORDER BY tariff_id
    """)
    print_table("ТАБЛИЦЯ: ТАРИФИ (tariffs)", columns, rows)
    
    # Телефони
    columns, rows = execute_query(cursor, """
        SELECT p.phone_number AS "Номер телефону", 
               p.client_id AS "Код клієнта",
               c.last_name || ' ' || c.first_name AS "Клієнт"
        FROM phones p
        JOIN clients c ON p.client_id = c.client_id
        ORDER BY p.client_id, p.phone_number
    """)
    print_table("ТАБЛИЦЯ: ТЕЛЕФОНИ (phones)", columns, rows)
    
    # Розмови
    columns, rows = execute_query(cursor, """
        SELECT c.call_id AS "Код розмови", 
               c.call_date AS "Дата розмови", 
               c.phone_number AS "Номер телефону",
               c.duration_minutes AS "Тривалість (хв)", 
               t.call_type AS "Тип дзвінка"
        FROM calls c
        JOIN tariffs t ON c.tariff_id = t.tariff_id
        ORDER BY c.call_date, c.call_id
    """)
    print_table("ТАБЛИЦЯ: РОЗМОВИ (calls)", columns, rows)


# Запит 1: Фізичні особи, сортування по прізвищу
def query_1_physical_persons(cursor):
    columns, rows = execute_query(cursor, """
        SELECT client_id AS "Код клієнта", 
               last_name AS "Прізвище", 
               first_name AS "Ім'я", 
               middle_name AS "По батькові",
               address AS "Адреса"
        FROM clients
        WHERE client_type = 'фізична особа'
        ORDER BY last_name
    """)
    print_table("ЗАПИТ 1: Клієнти - фізичні особи (сортування за прізвищем)", columns, rows)


# Запит 2: Кількість клієнтів за типом (підсумковий)
def query_2_count_by_type(cursor):
    columns, rows = execute_query(cursor, """
        SELECT client_type AS "Тип клієнта", 
               COUNT(*) AS "Кількість клієнтів"
        FROM clients
        GROUP BY client_type
        ORDER BY client_type
    """)
    print_table("ЗАПИТ 2: Кількість клієнтів за типом (підсумковий запит)", columns, rows)


# Запит 3: Вартість розмови (обчислювальне поле)
def query_3_call_cost(cursor):
    columns, rows = execute_query(cursor, """
        SELECT c.call_id AS "Код розмови",
               c.call_date AS "Дата",
               c.phone_number AS "Номер телефону",
               t.call_type AS "Тип дзвінка",
               c.duration_minutes AS "Хвилин",
               t.price_per_minute AS "Тариф (грн/хв)",
               ROUND(c.duration_minutes * t.price_per_minute, 2) AS "Вартість (грн)"
        FROM calls c
        JOIN tariffs t ON c.tariff_id = t.tariff_id
        ORDER BY c.call_date, c.call_id
    """)
    print_table("ЗАПИТ 3: Вартість кожної розмови (обчислювальне поле)", columns, rows)


# Запит 4: Розмови за типом дзвінка (параметризований)
def query_4_calls_by_type(cursor, call_type):
    columns, rows = execute_query(cursor, """
        SELECT c.call_id AS "Код розмови",
               c.call_date AS "Дата",
               c.phone_number AS "Номер телефону",
               cl.last_name || ' ' || cl.first_name AS "Клієнт",
               c.duration_minutes AS "Хвилин",
               t.call_type AS "Тип дзвінка"
        FROM calls c
        JOIN tariffs t ON c.tariff_id = t.tariff_id
        JOIN phones p ON c.phone_number = p.phone_number
        JOIN clients cl ON p.client_id = cl.client_id
        WHERE t.call_type = %s
        ORDER BY c.call_date
    """, (call_type,))
    print_table(f"ЗАПИТ 4: Розмови типу '{call_type}' (параметризований)", columns, rows)


# Запит 5: Загальна вартість для клієнта (підсумковий)
def query_5_total_cost_per_client(cursor):
    columns, rows = execute_query(cursor, """
        SELECT cl.client_id AS "Код клієнта",
               cl.last_name || ' ' || cl.first_name AS "Клієнт",
               cl.client_type AS "Тип клієнта",
               COUNT(c.call_id) AS "Кількість розмов",
               SUM(c.duration_minutes) AS "Всього хвилин",
               ROUND(SUM(c.duration_minutes * t.price_per_minute), 2) AS "Загальна вартість (грн)"
        FROM clients cl
        JOIN phones p ON cl.client_id = p.client_id
        JOIN calls c ON p.phone_number = c.phone_number
        JOIN tariffs t ON c.tariff_id = t.tariff_id
        GROUP BY cl.client_id, cl.last_name, cl.first_name, cl.client_type
        ORDER BY "Загальна вартість (грн)" DESC
    """)
    print_table("ЗАПИТ 5: Загальна вартість розмов клієнта (підсумковий)", columns, rows)


# Запит 6: Хвилини за типами для клієнта (перехресний)
def query_6_crosstab(cursor):
    columns, rows = execute_query(cursor, """
        SELECT cl.last_name || ' ' || cl.first_name AS "Клієнт",
               COALESCE(SUM(CASE WHEN t.call_type = 'внутрішній' THEN c.duration_minutes END), 0) AS "Внутрішні (хв)",
               COALESCE(SUM(CASE WHEN t.call_type = 'міжміський' THEN c.duration_minutes END), 0) AS "Міжміські (хв)",
               COALESCE(SUM(CASE WHEN t.call_type = 'мобільний' THEN c.duration_minutes END), 0) AS "Мобільні (хв)",
               SUM(c.duration_minutes) AS "Всього (хв)"
        FROM clients cl
        JOIN phones p ON cl.client_id = p.client_id
        JOIN calls c ON p.phone_number = c.phone_number
        JOIN tariffs t ON c.tariff_id = t.tariff_id
        GROUP BY cl.client_id, cl.last_name, cl.first_name
        ORDER BY cl.last_name
    """)
    print_table("ЗАПИТ 6: Хвилини за типами дзвінків (перехресний запит)", columns, rows)


# Головна функція
def main():
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  ЛАБОРАТОРНА РОБОТА №9  -  ТЕЛЕФОННА СТАНЦІЯ  ".center(78) + "#")
    print("#" + "  PostgreSQL + Python  ".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("\nПідключеня успішне!\n")
        
        # Вивід таблиць
        print("\n" + "~" * 80)
        print("  СТРУКТУРА ТА ДАНІ ТАБЛИЦЬ")
        print("~" * 80)
        display_all_tables(cursor)
        
        # Виконаня запитів
        print("\n" + "~" * 80)
        print("  РЕЗУЛЬТАТИ SQL ЗАПИТІВ")
        print("~" * 80)
        
        query_1_physical_persons(cursor)
        query_2_count_by_type(cursor)
        query_3_call_cost(cursor)
        
        # Запит з параметром для всіх типів
        for call_type in ['внутрішній', 'міжміський', 'мобільний']:
            query_4_calls_by_type(cursor, call_type)
        
        query_5_total_cost_per_client(cursor)
        query_6_crosstab(cursor)
        
        print("\n" + "#" * 80)
        print("#" + "  ПРОГРАМА ЗАВЕРШЕНА УСПІШНО  ".center(78) + "#")
        print("#" * 80 + "\n")
        
    except psycopg.Error as e:
        print(f"\nПомилка БД: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()

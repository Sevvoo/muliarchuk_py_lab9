# Головна програма для БД "Авто майстерня Ford" (Варіант 5)
# Виводить таблиці та виконуе SQL запити

import psycopg
from tabulate import tabulate


# Налаштування підключеня до БД
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'dbname': 'auto_workshop',
    'user': 'admin',
    'password': 'admin123'
}


# Підключеня до БД
def get_connection():
    return psycopg.connect(**DB_CONFIG)


# Виконати запит і повернути резултат
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
               company_name AS "Назва компанії", 
               account_number AS "Розрах. рахунок",
               phone AS "Телефон", 
               contact_person AS "Контактна особа", 
               address AS "Адреса"
        FROM clients
        ORDER BY client_id
    """)
    print_table("ТАБЛИЦЯ: КЛІЄНТИ (clients)", columns, rows)
    
    # Автомобілі
    columns, rows = execute_query(cursor, """
        SELECT c.car_id AS "Код авто", 
               c.car_model AS "Марка", 
               c.new_car_price AS "Вартість нового (грн)",
               c.client_id AS "Код клієнта",
               cl.company_name AS "Клієнт"
        FROM cars c
        JOIN clients cl ON c.client_id = cl.client_id
        ORDER BY c.car_id
    """)
    print_table("ТАБЛИЦЯ: АВТОМОБІЛІ (cars)", columns, rows)
    
    # Ремонти
    columns, rows = execute_query(cursor, """
        SELECT r.repair_id AS "Код ремонту", 
               r.start_date AS "Дата початку", 
               c.car_model AS "Марка авто",
               r.repair_type AS "Тип ремонту",
               r.hour_rate AS "Тариф (грн/год)",
               r.discount AS "Знижка (%)",
               r.hours_needed AS "Годин"
        FROM repairs r
        JOIN cars c ON r.car_id = c.car_id
        ORDER BY r.start_date, r.repair_id
    """)
    print_table("ТАБЛИЦЯ: РЕМОНТИ (repairs)", columns, rows)


# Запит 1: Гарантійні ремонти, сортувння по клієнту
def query_1_warranty_repairs(cursor):
    columns, rows = execute_query(cursor, """
        SELECT r.repair_id AS "Код ремонту",
               r.start_date AS "Дата",
               cl.company_name AS "Клієнт",
               c.car_model AS "Марка авто",
               r.hours_needed AS "Годин",
               r.hour_rate AS "Тариф"
        FROM repairs r
        JOIN cars c ON r.car_id = c.car_id
        JOIN clients cl ON c.client_id = cl.client_id
        WHERE r.repair_type = 'гарантійний'
        ORDER BY cl.company_name
    """)
    print_table("ЗАПИТ 1: Гарантійні ремонти (сортування за клієнтом)", columns, rows)


# Запит 2: Вартість ремонту з урахуваням знижки (обчислювальне поле)
def query_2_repair_cost(cursor):
    columns, rows = execute_query(cursor, """
        SELECT r.repair_id AS "Код ремонту",
               c.car_model AS "Марка",
               r.repair_type AS "Тип ремонту",
               r.hour_rate AS "Тариф (грн/год)",
               r.hours_needed AS "Годин",
               r.discount AS "Знижка (%)",
               ROUND(r.hour_rate * r.hours_needed, 2) AS "Вартість (грн)",
               ROUND(r.hour_rate * r.hours_needed * (1 - r.discount/100), 2) AS "Зі знижкою (грн)"
        FROM repairs r
        JOIN cars c ON r.car_id = c.car_id
        ORDER BY r.repair_id
    """)
    print_table("ЗАПИТ 2: Вартість ремонту зі знижкою (обчислювальне поле)", columns, rows)


# Запит 3: Ремонти для заданої марки авто (параметризований)
def query_3_repairs_by_model(cursor, car_model):
    columns, rows = execute_query(cursor, """
        SELECT r.repair_id AS "Код ремонту",
               r.start_date AS "Дата",
               cl.company_name AS "Клієнт",
               c.car_model AS "Марка",
               r.repair_type AS "Тип",
               r.hours_needed AS "Годин",
               ROUND(r.hour_rate * r.hours_needed * (1 - r.discount/100), 2) AS "Вартість (грн)"
        FROM repairs r
        JOIN cars c ON r.car_id = c.car_id
        JOIN clients cl ON c.client_id = cl.client_id
        WHERE c.car_model = %s
        ORDER BY r.start_date
    """, (car_model,))
    print_table(f"ЗАПИТ 3: Ремонти для марки '{car_model}' (параметризований)", columns, rows)


# Запит 4: Загальна сума для кожного клієнта (підсумковий)
def query_4_total_per_client(cursor):
    columns, rows = execute_query(cursor, """
        SELECT cl.client_id AS "Код клієнта",
               cl.company_name AS "Клієнт",
               COUNT(r.repair_id) AS "Кількість ремонтів",
               ROUND(SUM(r.hour_rate * r.hours_needed * (1 - r.discount/100)), 2) AS "Загальна сума (грн)"
        FROM clients cl
        JOIN cars c ON cl.client_id = c.client_id
        JOIN repairs r ON c.car_id = r.car_id
        GROUP BY cl.client_id, cl.company_name
        ORDER BY "Загальна сума (грн)" DESC
    """)
    print_table("ЗАПИТ 4: Загальна сума сплачена кожним клієнтом (підсумковий)", columns, rows)


# Запит 5: Кількість типів ремонту для клієнта (перехресний)
def query_5_crosstab(cursor):
    columns, rows = execute_query(cursor, """
        SELECT cl.company_name AS "Клієнт",
               COALESCE(SUM(CASE WHEN r.repair_type = 'гарантійний' THEN 1 END), 0) AS "Гарантійний",
               COALESCE(SUM(CASE WHEN r.repair_type = 'плановий' THEN 1 END), 0) AS "Плановий",
               COALESCE(SUM(CASE WHEN r.repair_type = 'капітальний' THEN 1 END), 0) AS "Капітальний",
               COUNT(r.repair_id) AS "Всього"
        FROM clients cl
        JOIN cars c ON cl.client_id = c.client_id
        JOIN repairs r ON c.car_id = r.car_id
        GROUP BY cl.client_id, cl.company_name
        ORDER BY cl.company_name
    """)
    print_table("ЗАПИТ 5: Кількість типів ремонту для клієнта (перехресний)", columns, rows)


# Запит 6: Кількість ремонтів для кожної марки
def query_6_repairs_by_model(cursor):
    columns, rows = execute_query(cursor, """
        SELECT c.car_model AS "Марка автомобіля",
               COUNT(r.repair_id) AS "Кількість ремонтів",
               ROUND(AVG(r.hours_needed), 1) AS "Середня к-ть годин",
               ROUND(SUM(r.hour_rate * r.hours_needed * (1 - r.discount/100)), 2) AS "Загальна сума (грн)"
        FROM cars c
        JOIN repairs r ON c.car_id = r.car_id
        GROUP BY c.car_model
        ORDER BY "Кількість ремонтів" DESC
    """)
    print_table("ЗАПИТ 6: Кількість ремонтів для кожної марки", columns, rows)


# Головна функція
def main():
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  ЛАБОРАТОРНА РОБОТА №9  -  АВТО МАЙСТЕРНЯ FORD  ".center(78) + "#")
    print("#" + "  PostgreSQL + Python (Варіант 5)  ".center(78) + "#")
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
        
        query_1_warranty_repairs(cursor)
        query_2_repair_cost(cursor)
        
        # Запит з параметром для всіх марок
        for model in ['fiesta', 'focus', 'fusion', 'mondeo']:
            query_3_repairs_by_model(cursor, model)
        
        query_4_total_per_client(cursor)
        query_5_crosstab(cursor)
        query_6_repairs_by_model(cursor)
        
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

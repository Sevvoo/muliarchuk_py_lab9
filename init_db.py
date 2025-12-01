# Ініціалізаця БД "Авто майстерня Ford" (Варіант 5)
# Створюе таблиці та заповнює тестовими данними

import psycopg


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


# Створеня таблиць
def create_tables(cursor):
    
    # Видаленя старих таблиць
    cursor.execute("""
        DROP TABLE IF EXISTS repairs CASCADE;
        DROP TABLE IF EXISTS cars CASCADE;
        DROP TABLE IF EXISTS clients CASCADE;
    """)
    
    # Клієнти
    cursor.execute("""
        CREATE TABLE clients (
            client_id SERIAL PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            account_number VARCHAR(30) NOT NULL,
            phone VARCHAR(20) NOT NULL CHECK (phone ~ '^\\+38\\(0[0-9]{2}\\)[0-9]{3}-[0-9]{2}-[0-9]{2}$'),
            contact_person VARCHAR(100) NOT NULL,
            address VARCHAR(200) NOT NULL
        );
        
        COMMENT ON TABLE clients IS 'Клієнти авто майстерні';
        COMMENT ON COLUMN clients.client_id IS 'Код клієнта (PK)';
        COMMENT ON COLUMN clients.company_name IS 'Назва компанії клієнта';
        COMMENT ON COLUMN clients.account_number IS 'Розрахунковий рахунок';
        COMMENT ON COLUMN clients.phone IS 'Телефон (маска: +38(0XX)XXX-XX-XX)';
        COMMENT ON COLUMN clients.contact_person IS 'Контактна особа';
        COMMENT ON COLUMN clients.address IS 'Адреса';
    """)
    
    # Автомобілі
    cursor.execute("""
        CREATE TABLE cars (
            car_id SERIAL PRIMARY KEY,
            car_model VARCHAR(20) NOT NULL CHECK (car_model IN ('fiesta', 'focus', 'fusion', 'mondeo')),
            new_car_price DECIMAL(12, 2) NOT NULL CHECK (new_car_price > 0),
            client_id INTEGER NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(client_id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        
        COMMENT ON TABLE cars IS 'Автомобілі клієнтів';
        COMMENT ON COLUMN cars.car_id IS 'Код автомобіля (PK)';
        COMMENT ON COLUMN cars.car_model IS 'Марка: fiesta/focus/fusion/mondeo';
        COMMENT ON COLUMN cars.new_car_price IS 'Вартість нової машини';
        COMMENT ON COLUMN cars.client_id IS 'Код клієнта (FK)';
    """)
    
    # Ремонти
    cursor.execute("""
        CREATE TABLE repairs (
            repair_id SERIAL PRIMARY KEY,
            start_date DATE NOT NULL,
            car_id INTEGER NOT NULL,
            repair_type VARCHAR(20) NOT NULL CHECK (repair_type IN ('гарантійний', 'плановий', 'капітальний')),
            hour_rate DECIMAL(10, 2) NOT NULL CHECK (hour_rate > 0),
            discount DECIMAL(5, 2) NOT NULL DEFAULT 0 
                CHECK (discount >= 0 AND discount <= 10),
            hours_needed INTEGER NOT NULL CHECK (hours_needed > 0),
            FOREIGN KEY (car_id) REFERENCES cars(car_id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        
        COMMENT ON TABLE repairs IS 'Ремонти автомобілів';
        COMMENT ON COLUMN repairs.repair_id IS 'Код ремонту (PK)';
        COMMENT ON COLUMN repairs.start_date IS 'Дата початку ремонту';
        COMMENT ON COLUMN repairs.car_id IS 'Код автомобіля (FK)';
        COMMENT ON COLUMN repairs.repair_type IS 'Тип: гарантійний/плановий/капітальний';
        COMMENT ON COLUMN repairs.hour_rate IS 'Вартість години ремонту';
        COMMENT ON COLUMN repairs.discount IS 'Знижка 0-10% (обмеженя!)';
        COMMENT ON COLUMN repairs.hours_needed IS 'Кількість годин для ремонту';
    """)
    
    # Індекси для швидкого пошу|ку
    cursor.execute("""
        CREATE INDEX idx_clients_company ON clients(company_name);
        CREATE INDEX idx_cars_model ON cars(car_model);
        CREATE INDEX idx_repairs_type ON repairs(repair_type);
        CREATE INDEX idx_repairs_date ON repairs(start_date);
    """)
    
    print("Таблиці створено!")


# Заповненя тестовими данними
def insert_data(cursor):
    
    # 6 клієнтів
    clients_data = [
        ('ТОВ Авто-Люкс', 'UA123456789012345678901234', '+38(044)123-45-67', 'Шевченко Тарас', 'м. Київ, вул. Хрещатик, 1'),
        ('ФОП Іваненко', 'UA987654321098765432109876', '+38(032)234-56-78', 'Іваненко Петро', 'м. Львів, вул. Свободи, 25'),
        ('АТ Укравто', 'UA111222333444555666777888', '+38(048)345-67-89', 'Міщенко Олег', 'м. Одеса, вул. Дерибасівська, 10'),
        ('ТОВ Транс-Сервіс', 'UA222333444555666777888999', '+38(057)456-78-90', 'Коваленко Марія', 'м. Харків, пл. Свободи, 5'),
        ('ФОП Бондаренко', 'UA333444555666777888999000', '+38(056)567-89-01', 'Бондаренко Сергій', 'м. Дніпро, просп. Гагаріна, 100'),
        ('ТОВ ФордЦентр', 'UA444555666777888999000111', '+38(061)678-90-12', 'Петренко Анна', 'м. Запоріжжя, вул. Соборна, 50'),
    ]
    
    cursor.executemany("""
        INSERT INTO clients (company_name, account_number, phone, contact_person, address)
        VALUES (%s, %s, %s, %s, %s)
    """, clients_data)
    print("Додано 6 клієнтів")
    
    # Автомобілі (4 марки, різні клієнти)
    cars_data = [
        ('fiesta', 450000.00, 1),
        ('focus', 650000.00, 1),
        ('mondeo', 950000.00, 2),
        ('fusion', 800000.00, 2),
        ('fiesta', 480000.00, 3),
        ('focus', 700000.00, 3),
        ('mondeo', 1000000.00, 4),
        ('fusion', 850000.00, 4),
        ('fiesta', 420000.00, 5),
        ('focus', 620000.00, 5),
        ('mondeo', 980000.00, 6),
        ('fusion', 820000.00, 6),
    ]
    
    cursor.executemany("""
        INSERT INTO cars (car_model, new_car_price, client_id)
        VALUES (%s, %s, %s)
    """, cars_data)
    print("Додано 12 автомобілів")
    
    # 15 ремонтів
    repairs_data = [
        ('2025-10-05', 1, 'гарантійний', 500.00, 0, 3),
        ('2025-10-10', 2, 'плановий', 450.00, 5, 8),
        ('2025-10-15', 3, 'капітальний', 600.00, 10, 24),
        ('2025-10-18', 4, 'гарантійний', 550.00, 0, 4),
        ('2025-10-22', 5, 'плановий', 480.00, 7, 6),
        ('2025-11-01', 6, 'капітальний', 650.00, 8, 32),
        ('2025-11-05', 7, 'гарантійний', 520.00, 0, 5),
        ('2025-11-08', 8, 'плановий', 470.00, 5, 10),
        ('2025-11-10', 9, 'капітальний', 580.00, 10, 20),
        ('2025-11-12', 10, 'гарантійний', 510.00, 0, 2),
        ('2025-11-15', 11, 'плановий', 490.00, 6, 12),
        ('2025-11-18', 12, 'капітальний', 620.00, 9, 28),
        ('2025-11-20', 1, 'плановий', 460.00, 4, 7),
        ('2025-11-22', 3, 'гарантійний', 530.00, 0, 3),
        ('2025-11-25', 5, 'плановий', 475.00, 5, 9),
    ]
    
    cursor.executemany("""
        INSERT INTO repairs (start_date, car_id, repair_type, hour_rate, discount, hours_needed)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, repairs_data)
    print("Додано 15 ремонтів")


# Головна функція
def main():
    print("=" * 60)
    print("Ініціалізація БД 'Авто майстерня Ford'")
    print("=" * 60)
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("\nСтвореня таблиць...")
        create_tables(cursor)
        
        print("\nЗаповненя даними...")
        insert_data(cursor)
        
        conn.commit()
        print("\n" + "=" * 60)
        print("БД успішно ініціалізовано!")
        print("=" * 60)
        
    except psycopg.Error as e:
        print(f"\nПомилка БД: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()

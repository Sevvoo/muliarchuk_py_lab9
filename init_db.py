# Ініціалізація БД "Телефонна станція" (Варіант 9)
# Створює таблиці та заповнює тестовими данними

import psycopg


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


# Створеня таблиць
def create_tables(cursor):
    
    # Видаленя старих таблиць
    cursor.execute("""
        DROP TABLE IF EXISTS calls CASCADE;
        DROP TABLE IF EXISTS phones CASCADE;
        DROP TABLE IF EXISTS tariffs CASCADE;
        DROP TABLE IF EXISTS clients CASCADE;
    """)
    
    # Клієнти
    cursor.execute("""
        CREATE TABLE clients (
            client_id SERIAL PRIMARY KEY,
            client_type VARCHAR(20) NOT NULL CHECK (client_type IN ('відомство', 'фізична особа')),
            address VARCHAR(200) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50)
        );
        
        COMMENT ON TABLE clients IS 'Клієнти телефоної станції';
        COMMENT ON COLUMN clients.client_id IS 'Код клієнта (PK)';
        COMMENT ON COLUMN clients.client_type IS 'Тип: відомство/фізична особа';
        COMMENT ON COLUMN clients.address IS 'Адреса';
        COMMENT ON COLUMN clients.last_name IS 'Прізвище';
        COMMENT ON COLUMN clients.first_name IS 'Імя';
        COMMENT ON COLUMN clients.middle_name IS 'По батькові';
    """)
    
    # Тарифи
    cursor.execute("""
        CREATE TABLE tariffs (
            tariff_id SERIAL PRIMARY KEY,
            call_type VARCHAR(20) NOT NULL CHECK (call_type IN ('внутрішній', 'міжміський', 'мобільний')),
            price_per_minute DECIMAL(10, 2) NOT NULL CHECK (price_per_minute > 0),
            UNIQUE (call_type)
        );
        
        COMMENT ON TABLE tariffs IS 'Тарифи на дзвінки';
        COMMENT ON COLUMN tariffs.tariff_id IS 'Код тарифу (PK)';
        COMMENT ON COLUMN tariffs.call_type IS 'Тип: внутрішній/міжміський/мобільний';
        COMMENT ON COLUMN tariffs.price_per_minute IS 'Ціна за хвилину (грн)';
    """)
    
    # Телефони
    cursor.execute("""
        CREATE TABLE phones (
            phone_number VARCHAR(15) PRIMARY KEY,
            client_id INTEGER NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(client_id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        
        COMMENT ON TABLE phones IS 'Номери телефонів абонентів';
        COMMENT ON COLUMN phones.phone_number IS 'Номер телефона (PK)';
        COMMENT ON COLUMN phones.client_id IS 'Код клієнта (FK)';
    """)
    
    # Розмови
    cursor.execute("""
        CREATE TABLE calls (
            call_id SERIAL PRIMARY KEY,
            call_date DATE NOT NULL,
            phone_number VARCHAR(15) NOT NULL,
            duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
            tariff_id INTEGER NOT NULL,
            FOREIGN KEY (phone_number) REFERENCES phones(phone_number) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (tariff_id) REFERENCES tariffs(tariff_id) 
                ON DELETE RESTRICT ON UPDATE CASCADE
        );
        
        COMMENT ON TABLE calls IS 'Телефоні розмови';
        COMMENT ON COLUMN calls.call_id IS 'Код розмови (PK)';
        COMMENT ON COLUMN calls.call_date IS 'Дата';
        COMMENT ON COLUMN calls.phone_number IS 'Номер телефона (FK)';
        COMMENT ON COLUMN calls.duration_minutes IS 'Тривалість (хв)';
        COMMENT ON COLUMN calls.tariff_id IS 'Код тарифу (FK)';
    """)
    
    # Індекси для швидкого пошу|ку
    cursor.execute("""
        CREATE INDEX idx_clients_type ON clients(client_type);
        CREATE INDEX idx_clients_last_name ON clients(last_name);
        CREATE INDEX idx_calls_date ON calls(call_date);
        CREATE INDEX idx_calls_phone ON calls(phone_number);
    """)
    
    print("Таблиці створено!")


# Заповненя тестовими даними
def insert_data(cursor):
    
    # 5 клієнтів
    clients_data = [
        ('фізична особа', 'м. Київ, вул. Хрещатик, 1', 'Шевченко', 'Тарас', 'Григорович'),
        ('фізична особа', 'м. Львів, вул. Свободи, 25', 'Франко', 'Іван', 'Якович'),
        ('відомство', 'м. Одеса, вул. Дерибасівська, 10', 'Міненко', 'Олег', 'Петрович'),
        ('фізична особа', 'м. Харків, пл. Свободи, 5', 'Коваленко', 'Марія', 'Іванівна'),
        ('відомство', 'м. Дніпро, просп. Гагаріна, 100', 'Бондаренко', 'Сергій', 'Олександрович'),
    ]
    
    cursor.executemany("""
        INSERT INTO clients (client_type, address, last_name, first_name, middle_name)
        VALUES (%s, %s, %s, %s, %s)
    """, clients_data)
    print("Додано 5 клієнтів")
    
    # 3 тарифи
    tariffs_data = [
        ('внутрішній', 0.50),
        ('міжміський', 2.00),
        ('мобільний', 1.50),
    ]
    
    cursor.executemany("""
        INSERT INTO tariffs (call_type, price_per_minute)
        VALUES (%s, %s)
    """, tariffs_data)
    print("Додано 3 тарифи")
    
    # 7 номерів телефонів
    phones_data = [
        ('044-123-45-67', 1),
        ('044-234-56-78', 1),
        ('032-345-67-89', 2),
        ('048-456-78-90', 3),
        ('048-567-89-01', 3),
        ('057-678-90-12', 4),
        ('056-789-01-23', 5),
    ]
    
    cursor.executemany("""
        INSERT INTO phones (phone_number, client_id)
        VALUES (%s, %s)
    """, phones_data)
    print("Додано 7 номерів")
    
    # 20 розмов (листопад 2025)
    calls_data = [
        ('2025-11-01', '044-123-45-67', 5, 1),
        ('2025-11-02', '044-123-45-67', 15, 2),
        ('2025-11-03', '044-234-56-78', 8, 3),
        ('2025-11-05', '044-123-45-67', 3, 1),
        ('2025-11-04', '032-345-67-89', 10, 2),
        ('2025-11-06', '032-345-67-89', 7, 3),
        ('2025-11-10', '032-345-67-89', 12, 1),
        ('2025-11-07', '048-456-78-90', 20, 2),
        ('2025-11-08', '048-567-89-01', 5, 1),
        ('2025-11-12', '048-456-78-90', 30, 3),
        ('2025-11-15', '048-567-89-01', 25, 2),
        ('2025-11-09', '057-678-90-12', 6, 3),
        ('2025-11-11', '057-678-90-12', 4, 1),
        ('2025-11-14', '057-678-90-12', 18, 2),
        ('2025-11-18', '057-678-90-12', 9, 3),
        ('2025-11-13', '056-789-01-23', 45, 2),
        ('2025-11-16', '056-789-01-23', 15, 1),
        ('2025-11-20', '056-789-01-23', 22, 3),
        ('2025-11-25', '056-789-01-23', 8, 1),
        ('2025-11-28', '056-789-01-23', 35, 2),
    ]
    
    cursor.executemany("""
        INSERT INTO calls (call_date, phone_number, duration_minutes, tariff_id)
        VALUES (%s, %s, %s, %s)
    """, calls_data)
    print("Додано 20 розмов")


# Головна функція
def main():
    print("=" * 60)
    print("Ініціалізація БД 'Телефонна станція'")
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

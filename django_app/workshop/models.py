from django.db import models


class Client(models.Model):
    client_id = models.AutoField(primary_key=True, verbose_name='Код клієнта')
    company_name = models.CharField(
        max_length=100, 
        verbose_name='Назва компанії',
        help_text='Наприклад: ТОВ Авто-Люкс, ФОП Іваненко'
    )
    account_number = models.CharField(
        max_length=30, 
        verbose_name='Розрахунковий рахунок',
        help_text='Формат: UA + 27 цифр (наприклад: UA123456789012345678901234)'
    )
    phone = models.CharField(
        max_length=20, 
        verbose_name='Телефон',
        help_text='Формат: +38(0XX)XXX-XX-XX (наприклад: +38(067)123-45-67)'
    )
    contact_person = models.CharField(
        max_length=100, 
        verbose_name='Контактна особа',
        help_text='ПІБ контактної особи'
    )
    address = models.CharField(
        max_length=200, 
        verbose_name='Адреса',
        help_text='Повна адреса компанії'
    )

    class Meta:
        db_table = 'clients'
        managed = False
        verbose_name = 'Клієнт'
        verbose_name_plural = 'Клієнти'

    def __str__(self):
        return self.company_name


class Car(models.Model):
    CAR_MODELS = [
        ('fiesta', 'Ford Fiesta'),
        ('focus', 'Ford Focus'),
        ('fusion', 'Ford Fusion'),
        ('mondeo', 'Ford Mondeo'),
    ]
    
    car_id = models.AutoField(primary_key=True, verbose_name='Код автомобіля')
    car_model = models.CharField(
        max_length=20, 
        verbose_name='Марка автомобіля',
        help_text='Виберіть одну з моделей Ford: fiesta, focus, fusion, mondeo',
        choices=CAR_MODELS
    )
    new_car_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name='Вартість нового авто (грн)',
        help_text='Вартість нового автомобіля в гривнях'
    )
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        db_column='client_id',
        verbose_name='Клієнт'
    )

    class Meta:
        db_table = 'cars'
        managed = False
        verbose_name = 'Автомобіль'
        verbose_name_plural = 'Автомобілі'

    def __str__(self):
        return f"{self.get_car_model_display()} ({self.client.company_name})"


class Repair(models.Model):
    REPAIR_TYPES = [
        ('гарантійний', 'Гарантійний'),
        ('плановий', 'Плановий'),
        ('капітальний', 'Капітальний'),
    ]
    
    repair_id = models.AutoField(primary_key=True, verbose_name='Код ремонту')
    start_date = models.DateField(verbose_name='Дата початку', help_text='Дата початку ремонту')
    car = models.ForeignKey(
        Car, 
        on_delete=models.CASCADE, 
        db_column='car_id',
        verbose_name='Автомобіль'
    )
    repair_type = models.CharField(
        max_length=20, 
        verbose_name='Тип ремонту',
        help_text='Виберіть тип: гарантійний, плановий або капітальний',
        choices=REPAIR_TYPES
    )
    hour_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Тариф (грн/год)',
        help_text='Вартість однієї години ремонту в гривнях'
    )
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='Знижка (%)',
        help_text='Знижка від 0% до 10%'
    )
    hours_needed = models.IntegerField(
        verbose_name='Кількість годин',
        help_text='Скільки годин потрібно для ремонту'
    )

    class Meta:
        db_table = 'repairs'
        managed = False
        verbose_name = 'Ремонт'
        verbose_name_plural = 'Ремонти'

    def __str__(self):
        return f"Ремонт #{self.repair_id} ({self.get_repair_type_display()})"

    @property
    def total_cost(self):
        return self.hour_rate * self.hours_needed

    @property
    def cost_with_discount(self):
        return self.total_cost * (1 - self.discount / 100)

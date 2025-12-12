from django.db import models


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    class Meta:
        db_table = 'clients'
        managed = False

    def __str__(self):
        return self.company_name


class Car(models.Model):
    car_id = models.AutoField(primary_key=True)
    car_model = models.CharField(max_length=20)
    new_car_price = models.DecimalField(max_digits=12, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client_id')

    class Meta:
        db_table = 'cars'
        managed = False

    def __str__(self):
        return f"{self.car_model} ({self.client.company_name})"


class Repair(models.Model):
    repair_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    car = models.ForeignKey(Car, on_delete=models.CASCADE, db_column='car_id')
    repair_type = models.CharField(max_length=20)
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    hours_needed = models.IntegerField()

    class Meta:
        db_table = 'repairs'
        managed = False

    def __str__(self):
        return f"Ремонт #{self.repair_id} ({self.repair_type})"

    @property
    def total_cost(self):
        return self.hour_rate * self.hours_needed

    @property
    def cost_with_discount(self):
        return self.total_cost * (1 - self.discount / 100)

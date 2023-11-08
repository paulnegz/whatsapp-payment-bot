from datetime import datetime
from uuid import uuid4
from backend.entities.db_driver import get_customer_entity
from backend.helper.my_types import PaymentType, SubscriptionResponse, Status
from backend.helper.utils import MONTH, MONTH_PRICE
from backend.helper.utils import get_current_date, add_days, create_date
from backend.bank_payment.BankPaymentFactory import BankPaymentFactory
from pony.orm import *
from pony.orm.dbapiprovider import OperationalError
from pathlib import Path, PosixPath, WindowsPath


@db_session()
def db_get_phone(phone_number, db) -> str:
    if not phone_number:
        return None
    query = "SELECT phone_number FROM Customers WHERE phone_number = $phone_number"
    phone_number = db.execute(query).fetchall()[0][0]
    return phone_number


@db_session()
def db_get_name(name, db) -> str:
    if not name:
        return None
    query = "SELECT username FROM Customers WHERE username = $name"
    name = db.execute(query).fetchall()[0][0]
    return name


@db_session()
def db_get_id(phone_number, name, db):
    if phone_number:
        query = "SELECT id FROM Customers WHERE phone_number = $phone_number"
    else:
        query = "SELECT id FROM Customers WHERE username = $name"
    db_id = db.execute(query).fetchall()[0][0]
    return db_id


class Customers:
    @staticmethod
    @db_session()
    def is_customer(phone_number: str, name, db) -> bool:
        if phone_number:
            query = "SELECT id FROM Customers WHERE phone_number = $phone_number"
        else:
            query = "SELECT id FROM Customers WHERE username = $name"
        try:
            result = db.execute(query).fetchall()
            return bool(result)
        except OperationalError:
            return False

    @staticmethod
    @db_session()
    def register_customer(number, name, customerEntity, db):
        if Customers.is_customers(number, name, db): raise (ValueError(f"customer with {number} exist!"))
        if not number and not name:
            return
        customersEntity(
            phone_number=number,
            username=name,
            active_sub=False,
            sub_exp_date=str(datetime(1999, 1, 1, 0, 0, 0)),
            last_payment_date=str(datetime(1999, 1, 1, 0, 0, 0))
        )

    def __init__(self, phone_number, name, db) -> None:
        self.db, self.seller_db_entity = db, get_seller_entity()
        self.phone = db_get_phone(phone_number, db)
        self.name = db_get_name(name, db)
        self.id = db_get_id(phone_number, name, db)
        self.exp_date = db_get_exp_date(phone_number, name, db)
        self.days_paid = 0

    @db_session()
    def add_payment(self, receipt_date):
        if self.phone:
            query = "SELECT payment_paths FROM Customers WHERE phone_number = $self.phone"
        else:
            query = "SELECT payment_paths FROM Customers WHERE username = $self.name"
        payment_paths = self.db.execute(query).fetchall()[0]
        if self.phone:
            update_query = f"UPDATE Customers SET payment_paths={True} WHERE phone_number=:self.phone"
        else:
            update_query = f"UPDATE Customers SET payment_paths={True} last_payment_date=':receipt_date' WHERE username=:self.name"

        self.db.execute(update_query)

    def no_identifier(self) -> bool:
        return not self.phone and not self.name

    def success_message(self) -> str:
        return f'''Phone number: {self.phone}, you customer ID: is {self.id}'''


    def error_message(self, error_id) -> str:
        return f'''Phone number: {self.phone}, customers ID: {self.id}
Transaction failed, error code: {error_id}'''


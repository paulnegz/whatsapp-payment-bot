from pony.orm import set_sql_debug, Database
from pony.orm import *
from pony import orm


db = Database()
# set_sql_debug(True)
db.bind(provider='sqlite', filename="BANK_PAYMENTS.db", create_db=True)


def get_customer_entity(database):
    class Customers(database.Entity):
        _table_ = 'customers'
        id = orm.PrimaryKey(int, auto=True)
        phone_number = orm.Optional(str, 20, unique=True, nullable=True)
        username = orm.Optional(str, 30, nullable=True)
        payment_paths = orm.Required(StrArray)
        sales = orm.Set('Customers')
    return Customers


customersEntity = get_customer_entity(db)
db.generate_mapping(create_tables=True)

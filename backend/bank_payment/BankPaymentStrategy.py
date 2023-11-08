from abc import ABC, abstractmethod
from backend.helper.my_types import PaymentType
from backend.helper.utils import create_date
from datetime import datetime
import re


class BankPaymentInterface(ABC):
    def __init__(self, img_txt) -> None:
        self.img_txt = img_txt
        self.payment_type: PaymentType = self.get_payment_type()
        self.date: datetime = self.get_date()
        self.amount_paid: float = self.get_amount_paid()
        self.acc_num: str = self.get_account_number()

    def __repr__(self):
        return f'''
{self.payment_type}\nDate of transaction is: {self.date}
amount_paid: {self.amount_paid:,} to account number: {self.acc_num}
'''

    @abstractmethod
    def get_payment_type(self) -> PaymentType:
        pass

    @abstractmethod
    def get_amount_paid(self) -> float:
        pass

    @abstractmethod
    def get_date(self) -> datetime:
        pass
    
    @abstractmethod
    def get_account_number(self) -> str:
        pass


class AccessBankPayment(BankPaymentInterface):
    def __init__(self, img_txt) -> None:
        super().__init__(img_txt)

    def get_payment_type(self) -> PaymentType:
        return PaymentType.ACCESS

    def get_amount_paid(self) -> float:
        txt, search = self.img_txt, 'Transaction Amount.*'
        line = re.search(search, txt).group()[20:].replace(',', '')
        return float(line)

    def get_date(self) -> datetime:
        txt, search = self.img_txt, 'Transaction Date.*'
        line = re.search(search, txt).group()[17:27]
        return create_date(line)
    
    def get_account_number(self) -> str:
        return re.search("Beneficiary.*", self.img_txt).group()[12:]


class GTBankPayment(BankPaymentInterface):
    def __init__(self, img_txt) -> None:
        super().__init__(img_txt)

    def get_payment_type(self) -> PaymentType:
        return PaymentType.GTB

    def get_amount_paid(self) -> float:
        txt, search = self.img_txt, 'Amount.*'
        line = re.search(search, txt).group()[7:].replace(',', '').rstrip(" NGN")
        return float(line)

    def get_date(self) -> datetime:
        line = re.search("Paid On.*", self.img_txt).group()[8:19]
        return datetime.strptime(line, "%d %B %Y")    

    def get_account_number(self) -> str:
        line = re.search("Beneficiary.*", self.img_txt).group()[12:]
        return line


class OPAYBankPayment(BankPaymentInterface):
    def __init__(self, img_txt) -> None:
        super().__init__(img_txt)

    def get_payment_type(self) -> PaymentType:
        return PaymentType.OPAY

    def get_amount_paid(self) -> float:
        txt, search = self.img_txt, r'.*\sSUCCESS'
        line = re.search(search, txt).group().rstrip("SUCCESS")[1:].replace(',', '')
        return float(line)

    def get_date(self) -> datetime:
        txt, search = self.img_txt, r'SUCCESS\s.*'
        line = re.search(search, txt).group().lstrip("SUCCESS").lstrip()
        return datetime.strptime(line, "%b %d,%Y,%H:%M")

    def get_account_number(self) -> str:
        txt, search = self.img_txt, 'Recipient Details.*'
        line = re.search(search, txt).group()[18:].lstrip()
        return line


# class ZenithBankPayment(BankPaymentInterface):
#     def __init__(self, img_txt) -> None:
#         super().__init__()
#         self.img_txt = img_txt
#         self.payment_type: PaymentType = self.get_payment_type()
#         self.date: datetime = self.get_date()
#         self.amount_paid: float = self.get_amount_paid()
#         self.acc_num: str = self.get_account_number()
#
#     def get_payment_type(self)->PaymentType:
#         return PaymentType.ZENITH
#
#     def get_amount_paid(self)->float:
#         line = re.search(".*", self.img_txt).group()
#         print(self.img_txt)
#         # print(line)
#         quit()
#
#     def get_date(self)->datetime:
#         line = re.search("Transaction Date: .*", img_text).group()[18:38]
#         return datetime.strptime(line, "%d-%b-%Y %H:%M:%S")
#
#     def get_account_number(self)->str:
#         line = re.search("SUCCESS\s.*", img_text).group().lstrip("SUCCESS").lstrip()
#         print("date")
#         print(img_text)
#         print(line)
#         quit()

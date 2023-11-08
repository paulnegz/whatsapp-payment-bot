from enum import Enum, unique


@unique
class SubscriptionType(Enum):
    BASIC = 1
    PREMIUM = 2


@unique
class PaymentType(Enum):
    ACCESS = 1
    GTB = 2
    OPAY = 3
    ZENITH = 4
    ANY = 5
    UNKNOWN = 6


@unique
class Status(Enum):
    OK = 200
    ERROR = 404
    IN_PROGRESS = 102
    NO_RESPONSE = 408


class ImageWhatsappDownload:
    def __init__(self, *args):
        self.phone, self.username = args[0], args[1]
        self.local_path, self.msg_time = args[2], args[3]
        self.img_hash = args[4]


class ParseBankPaymentRequest:
    def __init__(self, path):
        self.local_path = path


class ParseBankPaymentRequestList:
    def __init__(self, msg_list: ImageWhatsappDownload):
        self.msg_list = msg_list
        self.req_list = self.init_req_list()

    def __del__(self):
        self.req_list.clear()

    def init_req_list(self):
        req_list = []
        for req in self.msg_list:
            if not req:
                continue
            path = req.local_path
            req_list.append(ParseBankPaymentRequest(path))
        return req_list


class ParsedBankPaymentResponse:
    def __init__(self, *_):
        self.txt = ""
        self.STATUS = Status.IN_PROGRESS

    def set_status(self, status):
        self.STATUS: Status = status
        if status == Status.NO_RESPONSE:
            self.txt = ""
        elif status == Status.ERROR:
            self.txt = "CAN NOT PROCESS BANK PAYMENT"
        return self

    def set_message(self, txt):
        self.txt = txt
        return self


class ParsedBankPaymentResponseList:
    def __init__(self, res_list):
        self.res_list = res_list

    def __del__(self):
        self.res_list.clear()


class SubscriptionRequest:
    def __init__(self, phone, user, path):
        self.phone, self.username = phone, user
        self.local_path = path


class SubscriptionRequestList:
    def __init__(self, msg_list: ImageWhatsappDownload):
        self.msg_list = msg_list
        self.req_list = self.init_req_list()

    def __del__(self):
        self.req_list.clear()

    def init_req_list(self):
        req_list = []
        for req in self.msg_list:
            if not req:
                continue
            phone, user, path = req.phone, req.username, req.local_path
            req_list.append(SubscriptionRequest(phone, user, path))
        return req_list


class SubscriptionResponse:
    def __init__(self, *_):
        self.txt = ""
        self.STATUS = Status.IN_PROGRESS

    def set_status(self, status):
        self.STATUS: Status = status
        return self

    def set_message(self, txt):
        self.txt = txt
        return self


class SubscriptionResponseList:
    def __init__(self, res_list):
        self.res_list = res_list

    def __del__(self):
        self.res_list.clear()

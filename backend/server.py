from backend.entities.db_driver import sellersEntity, db
from backend.helper.my_types import ParseBankPaymentRequestList, ParsedBankPaymentResponseList
from backend.helper.my_types import ParseBankPaymentRequest, ParsedBankPaymentResponse, Status
from backend.bank_payment.BankPaymentFactory import BankPaymentFactory
from fastapi import FastAPI


app = FastAPI()


@app.get("/parse_bankpayments")
def parse_bank_payments(req: ParseBankPaymentRequestList) -> ParsedBankPaymentResponseList:
    res_list = [parse_bank_payment(x) for x in req.req_list]
    return ParsedBankPaymentResponseList(res_list)

@app.get("/parse_bankpayment")
def parse_bank_payment(img_info: ParseBankPaymentRequest) -> ParsedBankPaymentResponse:
    path = img_info.local_path
    receipt = BankPaymentFactory(path).create_payment()
    if not receipt:
        return ParsedBankPaymentResponse().set_status(Status.ERROR)

    info = str(receipt)
    return ParsedBankPaymentResponse().set_status(Status.OK).set_message(info)


import re
from PIL import Image
from backend.bank_payment.BankPaymentStrategy import *
from backend.config import tesseract_cmd_path
from pathlib import Path, PosixPath, WindowsPath
from pytesseract import image_to_string, pytesseract


class BankPaymentFactory:
    def __init__(self, img_path: PosixPath|WindowsPath):
        self.path = img_path
        self.img_text: str = self.process_image()

    def process_image(self) -> str:
        pytesseract.tesseract_cmd = tesseract_cmd_path
        return image_to_string(Image.open(self.path), lang="eng")
    
    def create_payment(self):
        txt = self.img_text
        def isAccess(): return bool(re.search("Generated from AccessMore.*", txt))
        def isGTB(): return bool(re.search(".*GTWorld.*", txt))
        def isOPay(): return bool(re.search(".*OPay Transaction Receipt.*", txt))
        def isZenith(): return bool(re.search(".*TRANSACTION RECEIPT Z ZENITH.*", txt))

        if isAccess(): return AccessBankPayment(txt)
        if isGTB(): return GTBankPayment(txt)
        if isOPay(): return OPAYBankPayment(txt)
        # if isZenith(): return ZenithBankPayment(txt)
        return

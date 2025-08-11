import re
from qr_payment_cz.exceptions import ParseException
from refdatatypes.safedatatypes import safe_int


class IBANCalculator:
    def __init__(
        self, account_prefix: int, account_number: int, bank_number: int
    ) -> None:
        self.account_prefix = account_prefix
        self.account_number = account_number
        self.bank_number = bank_number

    @classmethod
    def parse_account_number(cls, account_number: str) -> (str, str, str):
        r = re.compile(
            r"^(?P<account_prefix>\d{0,6}-)?(?P<account_no>\d{4,10})/(?P<bank_id>\d{4})$"
        )
        match = r.match(account_number)
        if match:
            match_gr = match.groupdict()
            results = (
                safe_int((match_gr["account_prefix"] or "000000-")[:-1]),
                safe_int(match_gr["account_no"]),
                safe_int(match_gr["bank_id"]),
            )
            if (not results[0] and all(results[1:])) or all(results):
                return f"{results[0]:06d}", f"{results[1]:010d}", f"{results[2]:04d}"
        raise ParseException(f"Invalid account number '{account_number}'")

    def calculate(self) -> str:
        """ """
        bk = self.bank_number
        cu = self.account_prefix
        ac = self.account_number
        di = self._calc(f"{bk}{cu}{ac}123500")
        di = 98 - di
        if di < 10:
            di = f"0{di}"
        ib = f"CZ{di}{bk}{cu}{ac}"
        ib = f"{ib[0:4]} {ib[4:8]} {ib[8:12]} {ib[12:16]} {ib[16:20]} {ib[20:]}"
        return ib

    @classmethod
    def _calc(cls, buf: str) -> int:
        index = 0
        pz = -1
        while index <= len(buf):
            if pz < 0:
                dividend = buf[index : index + 9]
                index += 9
            elif 0 <= pz <= 9:
                dividend = str(pz) + buf[index : index + 8]
                index += 8
            else:
                dividend = str(pz) + buf[index : index + 7]
                index += 7
            pz = int(dividend) % 97
        return pz

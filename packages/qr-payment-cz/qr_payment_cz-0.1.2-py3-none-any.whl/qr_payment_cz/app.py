from argparse import ArgumentParser, Namespace
from qr_payment_cz.str_generator import StrGenerator
import qrcode


class App:
    def __init__(self):
        self.app_args: Namespace = self._parse_args()

    @classmethod
    def _parse_args(cls) -> Namespace:
        arg_parser = ArgumentParser(
            "QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/"
        )
        arg_parser.add_argument(
            "-a",
            "--account",
            type=str,
            dest="account",
            required=False,
            help="Account number std bank account format",
        )
        arg_parser.add_argument(
            "-i",
            "--iban-account",
            type=str,
            dest="iban_acc",
            required=False,
            help="Account number in IBAN format",
        )
        arg_parser.add_argument(
            "-v",
            "--ammount-value",
            type=float,
            dest="ammount",
            required=True,
            help="Payment ammount",
        )
        arg_parser.add_argument(
            "-m",
            "--message",
            type=str,
            dest="message",
            required=False,
            help="Message text for payment",
        )
        arg_parser.add_argument(
            "-rn",
            "--receiver-name",
            type=str,
            dest="rn",
            required=False,
            help="Payment receiver name",
        )
        arg_parser.add_argument(
            "-vs",
            "--variable-symbol",
            type=int,
            dest="vs",
            required=False,
            help="Payment variable symbol",
        )
        arg_parser.add_argument(
            "-ss",
            "--specific-symbol",
            type=int,
            dest="ss",
            required=False,
            help="Payment specific symbol",
        )
        arg_parser.add_argument(
            "-ks",
            "--constant-symbol",
            type=int,
            dest="ks",
            required=False,
            help="Payment contant symbol",
        )
        arg_parser.add_argument(
            "-o",
            "--output-file",
            type=str,
            dest="output_file",
            required=False,
            help="Output PNG file path",
        )

        args = arg_parser.parse_args()
        if not args.account and not args.iban_acc:
            arg_parser._print_message("Account number or IBAN is required\n")
            arg_parser.print_usage()
            exit(1)

        return args

    def run(self):
        generator = StrGenerator(
            account=self.app_args.account,
            iban=self.app_args.iban_acc,
            ammount=self.app_args.ammount,
            message=self.app_args.message,
            rn=self.app_args.rn,
            vs=self.app_args.vs,
            ss=self.app_args.ss,
            ks=self.app_args.ks,
        )
        qr_code_str = generator.generate_string()
        print(f"QR code string:\n{qr_code_str}")

        if self.app_args.output_file:
            print(f"Generating QR code image '{self.app_args.output_file}'")
            img = qrcode.make(qr_code_str)
            img.save(self.app_args.output_file)

        print("DONE.")

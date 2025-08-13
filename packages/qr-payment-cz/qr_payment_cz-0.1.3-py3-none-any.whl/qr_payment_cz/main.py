from qr_payment_cz.app import App
from qr_payment_cz.exceptions import ParseException, PaymentException


def main():
    app = App()
    try:
        app.run()
    except (ParseException, PaymentException) as ex:
        print(f"Exception occured while processing payment: {ex}")
        exit(1)


if __name__ == "__main__":
    main()

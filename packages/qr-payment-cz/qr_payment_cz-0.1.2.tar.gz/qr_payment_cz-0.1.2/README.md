# QR Payment CZ

```bash
qr-payment-cz --help
```

```
usage: QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/ [-h] [-a ACCOUNT] [-i IBAN_ACC] -v AMMOUNT [-m MESSAGE] [-rn RN] [-vs VS] [-ss SS] [-ks KS] [-o OUTPUT_FILE]

options:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account number std bank account format
  -i IBAN_ACC, --iban-account IBAN_ACC
                        Account number in IBAN format
  -v AMMOUNT, --ammount-value AMMOUNT
                        Payment ammount
  -m MESSAGE, --message MESSAGE
                        Message text for payment
  -rn RN, --receiver-name RN
                        Payment receiver name
  -vs VS, --variable-symbol VS
                        Payment variable symbol
  -ss SS, --specific-symbol SS
                        Payment specific symbol
  -ks KS, --constant-symbol KS
                        Payment contant symbol
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output PNG file path
```
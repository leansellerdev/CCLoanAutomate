from core.web import CCLoanWeb
from core.models.debt import Debt


if __name__ == '__main__':
    try:
        debt = Debt()

        app = CCLoanWeb(debt=debt)
        app.cc_loan_parse("000526650927")

        print(debt.debt())
    except (KeyboardInterrupt, SystemExit) as err:
        print(err)

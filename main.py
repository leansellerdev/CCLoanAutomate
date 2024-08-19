from core.web import CCLoanWeb

if __name__ == '__main__':
    try:
        app = CCLoanWeb(detach=False)
        app.cc_loan_parse("000526650927")
    except (KeyboardInterrupt, SystemExit) as err:
        print(err)

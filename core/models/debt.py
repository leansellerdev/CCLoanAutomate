from core.utils.utils import format_number, format_date, calculate_service, calculate_state_duty

class Debt:
    def __init__(self, iin=None, name=None, phone_number=None, summa=None, date_of_credit=None,
                 credit_id=None, credit_duration=None, credit_reward=None, final_summa=None, credit_fee=None,
                 state_duty=None, notarial_fee=None, service=None, penalty=None, paybox=None
                 ):

        self.iin = iin
        self.name = name
        self.phone_number = phone_number
        self.summa = summa
        self.date_of_credit = date_of_credit
        self.credit_id = credit_id
        self.credit_duration = credit_duration
        self.credit_reward = credit_reward
        self.final_summa = final_summa
        self.credit_fee = credit_fee
        self.state_duty = state_duty
        self.notarial_fee = notarial_fee
        self.service = service
        self.penalty = penalty
        self.paybox = paybox

    def format_all(self) -> None:
        self.date_of_credit = format_date(self.date_of_credit)
        self.service = format_number(calculate_service(amount=self.final_summa, notarial=int(
                                                                      float(self.notarial_fee.replace(',', '')
                                                                            ))))
        self.state_duty = format_number(calculate_state_duty(amount=self.final_summa,
                                                                  notarial=int(
                                                                      float(self.notarial_fee.replace(',', '')
                                                                            ))))
        self.summa = format_number(self.summa)
        self.credit_reward = format_number(self.credit_reward)
        self.credit_fee = format_number(self.credit_fee)
        self.notarial_fee = format_number(self.notarial_fee)
        self.final_summa = format_number(self.final_summa)

    def debt(self):
        return (self.iin, self.name, self.phone_number, self.summa, self.date_of_credit, self.credit_id,
                self.credit_duration, self.credit_reward, self.final_summa, self.credit_fee, self.state_duty,
                self.notarial_fee, self.service, self.penalty, self.paybox)

    def dump(self) -> dict:
        return self.__dict__



class Debt:
    def __init__(self, iin=None, name=None, phone_number=None, summa=None, date_of_credit=None,
                 credit_id=None, credit_duration=None, credit_reward=None, final_summa=None, credit_fee=None,
                 state_duty=None, notarial_fee=None, service=None
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

    def debt(self):
        return (self.iin, self.name, self.phone_number, self.summa, self.date_of_credit, self.credit_id,
                self.credit_duration, self.credit_reward, self.final_summa, self.credit_fee, self.state_duty,
                self.notarial_fee, self.service)

from docx import Document

name = "Қадербек Назгүл Қадербек"
phone_number = "887787982513"
iin = "000526650927"
summa = "40000 (сорок тысяч) тенге"
date_of_credit = "«20» января 2023"
credit_id = "1371015"
credit_duration = "20"
credit_reward = "4889 (четыре тысячи восемьсот восемьдесят девять) тенге"
today_date = "«18» августа 2024"
final_summa = "44889 (сорок четыре тысячи восемьсот восемьдесят девять) тенге"
credit_fee = "0 () тенге"
state_duty = "5000 (пять тысяч) тенге"
notarial = "1337 (тысяча триста тридцать семь) тенге"


def fill_statement():
    template = Document("templates/statement_template.docx")

    for i, paragraph in enumerate(template.paragraphs):
        for run in paragraph.runs:
            run.font.highlight_color = None

            if i == 12:
                run.text = run.text.replace("name", name)

            if i == 13:
                run.text = run.text.replace("phonenumber", phone_number)

            if i == 14:
                run.text = run.text.replace("iin", iin)

            if i == 17:
                run.text = run.text.replace("mainsumma", summa)

            if i == 23:
                run.text = run.text.replace("dateofcredit", date_of_credit)
                run.text = run.text.replace("creditid", credit_id)
                run.text = run.text.replace("mainsumma", summa)
                run.text = run.text.replace("creditduration", credit_duration)
                run.text = run.text.replace("creditreward", credit_reward)

            if i == 45:
                run.text = run.text.replace("todaydate", today_date)
                run.text = run.text.replace("finalsumma", final_summa)

            if i == 46:
                run.text = run.text.replace("mainsumma", summa)
            if i == 47:
                run.text = run.text.replace("creditreward", credit_reward)
            if i == 48:
                run.text = run.text.replace("creditfee", credit_fee)

            if i == 51:
                run.text = run.text.replace("stateduty", state_duty)

            if i == 61:
                run.text = run.text.replace("name", name)
                run.text = run.text.replace("finalsumma", final_summa)

            if i == 63:
                run.text = run.text.replace("mainsumma", summa)
            if i == 64:
                run.text = run.text.replace("creditreward", credit_reward)
            if i == 65:
                run.text = run.text.replace("creditfee", credit_fee)

            if i == 67:
                run.text = run.text.replace("name", name)
                run.text = run.text.replace("stateduty", state_duty)

            if i == 68:
                run.text = run.text.replace("name", name)
                run.text = run.text.replace("notarial", notarial)

    template.save(f"templates/Исковое_Заявление_{name.replace(' ', '_')}.docx")


fill_statement()

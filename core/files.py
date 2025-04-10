import json
from datetime import datetime

from docx import Document

from core.models.debt import Debt
from core.utils.utils import format_date
from settings import TEMPLATES_DIR


def fill_statement(debt: Debt):
    template = Document(TEMPLATES_DIR / 'statement_template.docx')

    with open(f"statements/statement_info.json", 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(debt.dump(), indent=4, ensure_ascii=False, default=str))

    debt.format_all()

    for i, paragraph in enumerate(template.paragraphs):
        for run in paragraph.runs:
            run.font.highlight_color = None

            if i == 16:
                capitalized_name = [name.capitalize() for name in debt.name.split()]
                run.text = run.text.replace("name", ' '.join(capitalized_name))

            if i == 17:
                run.text = run.text.replace("phonenumber", debt.phone_number)

            if i == 18:
                run.text = run.text.replace("iin", debt.iin)

            if i == 21:
                run.text = run.text.replace("notarial_plus_mainsumma", debt.notarial_plus_mainsumma)

            if i == 27:
                run.text = run.text.replace("dateofcredit", debt.date_of_credit)
                run.text = run.text.replace("creditid", debt.credit_id)
                run.text = run.text.replace("mainsumma", debt.summa)
                run.text = run.text.replace("creditduration", debt.credit_duration)
                run.text = run.text.replace("creditreward", debt.credit_reward)

            if i == 49:
                run.text = run.text.replace("todaydate", format_date(datetime.today()))
                run.text = run.text.replace("finalsumma", debt.final_summa)

            if i == 50:
                run.text = run.text.replace("mainsumma", debt.summa)
            if i == 51:
                run.text = run.text.replace("creditreward", debt.credit_reward)
            if i == 52:
                run.text = run.text.replace("creditfee", debt.credit_fee)

            if i == 55:
                run.text = run.text.replace("stateduty", debt.state_duty)

            if i == 65:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("finalsumma", debt.final_summa)

            if i == 67:
                run.text = run.text.replace("mainsumma", debt.summa)
            if i == 68:
                run.text = run.text.replace("creditreward", debt.credit_reward)
            if i == 69:
                run.text = run.text.replace("creditfee", debt.credit_fee)

            if i == 71:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("stateduty", debt.state_duty)

            if i == 72:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("notarial", debt.notarial_fee)

            if i == 73:
                run.text = run.text.replace("service", debt.service)

    template.save(f"statements/Исковое_Заявление_{debt.iin}.docx")


if __name__ == '__main__':
    fill_statement(Debt())

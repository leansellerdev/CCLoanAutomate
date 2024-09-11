from datetime import datetime

from docx import Document

from core.models.debt import Debt
from core.utils.utils import format_date

from settings import STATEMENTS_DIR


def fill_statement(debt: Debt):
    template = Document("core/templates/statement_template.docx")

    for i, paragraph in enumerate(template.paragraphs):
        for run in paragraph.runs:
            run.font.highlight_color = None

            if i == 12:
                run.text = run.text.replace("name", debt.name)

            if i == 13:
                run.text = run.text.replace("phonenumber", debt.phone_number)

            if i == 14:
                run.text = run.text.replace("iin", debt.iin)

            if i == 17:
                run.text = run.text.replace("mainsumma", debt.final_summa)

            if i == 23:
                run.text = run.text.replace("dateofcredit", debt.date_of_credit)
                run.text = run.text.replace("creditid", debt.credit_id)
                run.text = run.text.replace("mainsumma", debt.summa)
                run.text = run.text.replace("creditduration", debt.credit_duration)
                run.text = run.text.replace("creditreward", debt.credit_reward)

            if i == 45:
                run.text = run.text.replace("todaydate", format_date(datetime.today()))
                run.text = run.text.replace("finalsumma", debt.final_summa)

            if i == 46:
                run.text = run.text.replace("mainsumma", debt.summa)
            if i == 47:
                run.text = run.text.replace("creditreward", debt.credit_reward)
            if i == 48:
                run.text = run.text.replace("creditfee", debt.credit_fee)

            if i == 51:
                run.text = run.text.replace("stateduty", debt.state_duty)

            if i == 61:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("finalsumma", debt.final_summa)

            if i == 63:
                run.text = run.text.replace("mainsumma", debt.summa)
            if i == 64:
                run.text = run.text.replace("creditreward", debt.credit_reward)
            if i == 65:
                run.text = run.text.replace("creditfee", debt.credit_fee)

            if i == 67:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("stateduty", debt.state_duty)

            if i == 68:
                run.text = run.text.replace("name", debt.name)
                run.text = run.text.replace("notarial", debt.notarial_fee)

    template.save(f"statements/Исковое_Заявление_{debt.iin}.docx")

import io
import json

import pytz
import xlsxwriter
from django.utils.timezone import datetime


def generate_result_as_excel(request, quiz, quizTaker, responses):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(name="Result")

    worksheet.set_column("A:A", 20)
    worksheet.set_column("B:B", 60)
    worksheet.set_column("D:H", 20)
    worksheet.set_column("J:K", 30)

    bold_format = workbook.add_format({"bold": True, "text_wrap": True,})
    bold_y_format = workbook.add_format({"bold": True, "top": 1, "bottom": 1,})
    green_format = workbook.add_format(
        {"bg_color": "#C6EFCE", "font_color": "#006100", "text_wrap": "true",}
    )
    green_y_format = workbook.add_format(
        {
            "bg_color": "#C6EFCE",
            "font_color": "#006100",
            "text_wrap": "true",
            "top": 1,
            "bottom": 1,
        }
    )
    green_bold_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#C6EFCE",
            "font_color": "#006100",
            "text_wrap": "true",
        }
    )
    red_format = workbook.add_format(
        {"bg_color": "#FFC7CE", "font_color": "#9C0006", "text_wrap": True,}
    )
    red_y_format = workbook.add_format(
        {
            "bg_color": "#FFC7CE",
            "font_color": "#9C0006",
            "text_wrap": "true",
            "top": 1,
            "bottom": 1,
        }
    )
    red_bold_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#FFC7CE",
            "font_color": "#9C0006",
            "text_wrap": "true",
        }
    )
    blue_format = workbook.add_format(
        {"bg_color": "#b4daff", "font_color": "#003171", "text_wrap": True,}
    )
    blue_y_format = workbook.add_format(
        {
            "bg_color": "#b4daff",
            "font_color": "#003171",
            "text_wrap": "true",
            "top": 1,
            "bottom": 1,
        }
    )
    blue_bold_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#b4daff",
            "font_color": "#003171",
            "text_wrap": "true",
        }
    )

    rNo = 1

    worksheet.merge_range(f"A{rNo}:B{rNo}", request.user.full_name, bold_format)
    rNo += 1
    worksheet.merge_range(
        f"A{rNo}:B{rNo}", f"{request.user.email.upper()}", bold_format
    )
    rNo += 1
    worksheet.merge_range(f"A{rNo}:B{rNo}", f"Quiz: {quiz.title}", bold_format)
    rNo += 1
    worksheet.merge_range(f"A{rNo}:B{rNo}", "")
    rNo += 1
    descLength = len(quiz.description.split("\n"))
    worksheet.merge_range(
        f"A{rNo}:B{rNo + descLength - 1}", f"{quiz.description}", bold_format
    )

    rNo += descLength + 1

    extra = json.loads(quizTaker.extra)
    for key, value in extra.items():
        worksheet.write(f"A{rNo}", f"{key}:", bold_format)
        worksheet.write(f"B{rNo}", f"{value}", bold_format)
        rNo += 1

    rNo += 1
    started = quizTaker.started.astimezone(tz=pytz.timezone(request.user.timeZone))
    try:
        started = datetime.strftime(started, "%Y-%m-%d %-I:%M:%S %p")
    except ValueError:
        started = datetime.strftime(started, "%Y-%m-%d %#I:%M:%S %p")
    worksheet.write(f"A{rNo}", "Started At:", bold_format)
    worksheet.write(f"B{rNo}", f"{started}", bold_format)

    rNo += 1
    ended = quizTaker.completed.astimezone(tz=pytz.timezone(request.user.timeZone))
    try:
        ended = datetime.strftime(ended, "%Y-%m-%d %-I:%M:%S %p")
    except ValueError:
        ended = datetime.strftime(ended, "%Y-%m-%d %#I:%M:%S %p")
    worksheet.write(f"A{rNo}", "Submitted At:", bold_format)
    worksheet.write(f"B{rNo}", f"{ended}", bold_format)
    rNo += 2

    total_marks = sum([r.question.marks for r in responses])
    marks_obtained = sum([q.marks for q in responses])
    worksheet.merge_range(f"A{rNo}:B{rNo}", f"Total Marks: {total_marks}", bold_format)
    rNo += 1
    worksheet.merge_range(
        f"A{rNo}:B{rNo}", f"Marks Obtained: {marks_obtained}", bold_format
    )
    rNo += 2
    if 100 * marks_obtained / total_marks > 33:
        worksheet.merge_range(f"A{rNo}:B{rNo}", f"Status: Passed", green_bold_format)
    else:
        worksheet.merge_range(f"A{rNo}:B{rNo}", f"Status: Failed", red_bold_format)

    rNo += 2
    worksheet.write(f"A{rNo}", "Que No.", bold_y_format)
    worksheet.write(f"B{rNo}", "Question Statement", bold_y_format)
    worksheet.write(f"C{rNo}", "", bold_y_format)
    worksheet.write(f"D{rNo}", "Option 1", bold_y_format)
    worksheet.write(f"E{rNo}", "Option 2", bold_y_format)
    worksheet.write(f"F{rNo}", "Option 3", bold_y_format)
    worksheet.write(f"G{rNo}", "Option 4", bold_y_format)
    worksheet.write(f"H{rNo}", "Option 5", bold_y_format)
    worksheet.write(f"I{rNo}", "", bold_y_format)
    worksheet.write(f"J{rNo}", "Correct Answer", bold_y_format)
    worksheet.write(f"K{rNo}", "Your Answer", bold_y_format)
    worksheet.write(f"L{rNo}", "Is Correct", bold_y_format)
    worksheet.write(f"M{rNo}", "Marks", bold_y_format)

    for i, response in enumerate(responses):
        rNo += 1
        if response.isCorrect:
            format = green_y_format
        else:
            if response.answer == "":
                format = blue_y_format
            else:
                format = red_y_format
        worksheet.write(f"A{rNo}", i + 1, format)
        worksheet.write(f"B{rNo}", f"{response.question.title}", format)
        worksheet.write(f"C{rNo}", "", format)
        worksheet.write(f"D{rNo}", f"{response.question.choice_1}", format)
        worksheet.write(f"E{rNo}", f"{response.question.choice_2}", format)
        worksheet.write(f"F{rNo}", f"{response.question.choice_3}", format)
        worksheet.write(f"G{rNo}", f"{response.question.choice_4}", format)
        worksheet.write(f"H{rNo}", f"{response.question.choice_5}", format)
        worksheet.write(f"I{rNo}", "", format)
        worksheet.write(f"J{rNo}", f"{response.question.correct}", format)
        worksheet.write(f"K{rNo}", f"{response.answer}", format)
        worksheet.write(f"L{rNo}", f"{response.isCorrect}", format)
        worksheet.write(f"M{rNo}", response.marks, format)

    workbook.close()

    output.seek(0)

    return output

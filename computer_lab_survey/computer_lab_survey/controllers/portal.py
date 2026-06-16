from odoo import http
from odoo.http import request


class ComputerLabSurveyPortal(http.Controller):
    DAYS = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
    ]
    SLOT_LABELS = [
        "8:00 - 10:00 am",
        "10:00 am - 12:00 pm",
        "12:00 - 2:00 pm",
        "2:00 - 4:00 pm",
        "4:00 - 6:00 pm",
    ]
    STATUSES = [
        ("free", "Free / Available"),
        ("class", "Scheduled Class"),
        ("exam", "Exam / Practical"),
        ("workshop", "Workshop / Event"),
        ("maintenance", "Maintenance / Closed"),
    ]

    def _selection(self, model_name, field_name):
        field = request.env[model_name]._fields[field_name]
        return list(field.selection)

    def _page_values(self, errors=None, form_values=None):
        Survey = request.env["computer.lab.survey"]
        default_academic_year = Survey._fields["academic_year"].default
        return {
            "errors": errors or [],
            "form_values": form_values or {},
            "college_options": self._selection("computer.lab.survey", "college"),
            "academic_year_options": self._selection("computer.lab.survey", "academic_year"),
            "sharable_options": self._selection("computer.lab.survey", "sharable"),
            "booking_notice_options": self._selection("computer.lab.survey", "booking_notice"),
            "status_options": self.STATUSES,
            "days": self.DAYS,
            "slot_labels": self.SLOT_LABELS,
            "slot_indices": list(range(5)),
            "default_academic_year": default_academic_year(Survey) if callable(default_academic_year) else default_academic_year,
        }

    @http.route("/computer-lab-survey", type="http", auth="public", website=True)
    def lab_survey_form(self, **kwargs):
        return request.render(
            "computer_lab_survey.portal_lab_survey_form",
            self._page_values(),
        )

    @http.route("/computer-lab-survey/submit", type="http", auth="public", website=True, methods=["POST"])
    def lab_survey_submit(self, **post):
        required = [
            "college",
            "department",
            "lab_name",
            "incharge_name",
            "contact_info",
            "week_start_date",
            "week_end_date",
            "academic_year",
        ]
        errors = ["%s is required." % name.replace("_", " ").title() for name in required if not post.get(name)]
        try:
            num_desktops = int(post.get("num_desktops") or 0)
        except ValueError:
            num_desktops = 0
        if num_desktops <= 0:
            errors.append("Number of desktops must be greater than zero.")

        if errors:
            return request.render(
                "computer_lab_survey.portal_lab_survey_form",
                self._page_values(errors=errors, form_values=post),
            )

        survey = request.env["computer.lab.survey"].sudo().create({
            "college": post.get("college"),
            "department": post.get("department"),
            "lab_name": post.get("lab_name"),
            "num_desktops": num_desktops,
            "incharge_name": post.get("incharge_name"),
            "contact_info": post.get("contact_info"),
            "week_start_date": post.get("week_start_date"),
            "week_end_date": post.get("week_end_date"),
            "academic_year": post.get("academic_year"),
            "sharable": post.get("sharable") or False,
            "booking_notice": post.get("booking_notice") or False,
            "special_conditions": post.get("special_conditions"),
            "infra_issues": post.get("infra_issues"),
        })

        slot_counters = {}
        for slot in survey.slot_ids.sorted(lambda item: (item.day_order, item.id)):
            slot_index = slot_counters.get(slot.day, 0)
            slot_counters[slot.day] = slot_index + 1
            key = "%s_%s" % (slot.day, slot_index)
            try:
                student_count = int(post.get("students_%s" % key) or 0)
            except ValueError:
                student_count = 0
            slot.write({
                "status": post.get("status_%s" % key) or "free",
                "course_subject": post.get("course_%s" % key),
                "batch_class": post.get("batch_%s" % key),
                "student_count": student_count,
            })

        survey.action_submit()
        return request.render(
            "computer_lab_survey.portal_lab_survey_thank_you",
            {"survey": survey},
        )

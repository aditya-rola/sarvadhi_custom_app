import frappe
from frappe.utils import today ,nowdate, getdate, add_days
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def get_upcoming_holidays():
    """Retrieve upcoming holidays based on the default holiday list for the user's company."""

    default_company = frappe.defaults.get_user_default("company")
    if not default_company:
        frappe.log_error("No default company set for the user.", "get_upcoming_holidays")
        return []

    company = frappe.get_all('Company', filters={'name': default_company}, fields=['default_holiday_list'])
    if not company:
        frappe.log_error(f"Company {default_company} not found.", "get_upcoming_holidays")
        return []

    holiday_list_name = company[0].get('default_holiday_list')
    if not holiday_list_name:
        frappe.log_error(f"No holiday list assigned to the company {default_company}.", "get_upcoming_holidays")
        return []

    try:
        holiday_obj = frappe.get_doc('Holiday List', holiday_list_name)
        today_date = datetime.strptime(today(), '%Y-%m-%d').date()
        holidays = holiday_obj.holidays

        upcoming_holidays = [
            {
                'holiday_name': holiday.description,  
                'holiday_date': holiday.holiday_date,
                'dayname': holiday.holiday_date.strftime('%A')
            }
            for holiday in holidays if holiday.holiday_date >= today_date
        ]
        return upcoming_holidays

    except frappe.DoesNotExistError:
        frappe.log_error(f"Holiday List {holiday_list_name} does not exist.", "get_upcoming_holidays")
        return []

    except Exception as e:
        frappe.log_error(f"Error fetching holidays for company {default_company}: {str(e)}", "get_upcoming_holidays")
        return []


@frappe.whitelist()
def get_upcoming_birthdays():
    """Fetch upcoming birthdays of users in the same company as the logged-in user."""

    default_company = frappe.defaults.get_user_default("company")

    birthdays = frappe.get_all("Employee",
        filters={
            "company": default_company,
            "status": "Active",
        },
        fields=["name", "employee_name", "date_of_birth","designation"],
        order_by="date_of_birth asc"
    )

    upcoming_birthdays = []
    today = getdate(nowdate())

    for emp in birthdays:
        if emp["date_of_birth"]:
            birth_date = getdate(emp["date_of_birth"]).replace(year=today.year)
            if birth_date >= today and birth_date <= add_days(today, 30):  # Get birthdays within the next 30 days
                upcoming_birthdays.append({
                    "employee_name": emp["employee_name"],
                    "date_of_birth": birth_date.strftime("%d-%b"),
                    "day_name": birth_date.strftime("%A"),
                    "designation": emp['designation']
                })

    if upcoming_birthdays:
        return upcoming_birthdays
    else:
        return {"message": "No upcoming birthdays in the next 30 days."}

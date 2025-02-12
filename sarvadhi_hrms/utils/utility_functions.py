import frappe
from frappe.utils import today
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


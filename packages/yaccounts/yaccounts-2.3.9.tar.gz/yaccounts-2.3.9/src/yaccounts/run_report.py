import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .config import get_verbose
from .chrome import goto_workday_page
from .table import (
    extract_actuals_from_activity_table,
    extract_actuals_from_grant_table,
    extract_journal_data_from_table,
    extract_payroll_data_from_table,
)
from .yutils import TermColors, print_color, print_progress

SLEEP_AFTER_GRANT = 1
SLEEP_AFTER_PERIOD = 3


################################################################################
############################# Report Functions #################################
################################################################################
def run_grant_report(dr, account, month_year):
    _configure_account_report(dr, "grant", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_grant_table(dr, month_year)
    print("Done")
    return ret


def run_activity_report(dr, account, month_year):
    _configure_account_report(dr, "activity", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_activity_table(dr, month_year)
    print("Done")
    return ret


def run_gift_report(dr, account, month_year):
    _configure_account_report(dr, "gift", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, "div.wd-DataGrid")
    ret = extract_actuals_from_activity_table(dr, month_year)
    print("Done")
    return ret


def run_journal_report(dr, account, month_year):
    _configure_account_report(dr, "journal", account, month_year)
    _run_report(dr)
    _wait_for_data_table(dr, 'table[data-testid="table"]')
    ret = extract_journal_data_from_table(dr)
    print("Done")
    return ret


def run_payroll_report(dr, year):
    print_color(
        TermColors.BLUE, "Running payroll report", end="\n" if get_verbose() else ""
    )
    goto_workday_page(dr)
    _goto_finance_reports(dr)
    _click_finance_report(dr, "BYU Payroll Details By Worktag")

    _set_date_by_label(dr, "Starting Accounting_Date", 1, 1, year)
    _set_date_by_label(dr, "Ending Accounting_Date", 12, 31, year)

    _run_report(dr)
    _wait_for_data_table(dr, 'table[data-testid="table"]')

    ret = extract_payroll_data_from_table(dr)
    print("Done")
    return ret


################################################################################
############################# Internal Helpers #################################
################################################################################


def _wait_for_data_table(dr, selector):
    # Wait for the data table to be present and visible
    WebDriverWait(dr, 30).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )
    print_progress("Data table is visible.")


def _configure_account_report(dr, type, account, month_year):
    print_color(
        TermColors.BLUE,
        f"Running {type.capitalize()} report for {account} {month_year.strftime('%b %Y')}",
        end="\n" if get_verbose() else "",
    )
    goto_workday_page(dr)
    _goto_finance_reports(dr)

    if type == "journal":
        _click_finance_report(dr, "BYU Find Journal Lines")
    else:
        _click_finance_report(
            dr, f"BYU Budget Vs Actuals Overview by {type.capitalize()}"
        )

    if type == "grant":
        account_select_input_id = "15$394423"
    elif type in ("activity", "gift"):
        account_select_input_id = "15$160390"
    elif type == "journal":
        account_select_input_id = "15$163517"
    else:
        raise ValueError(f"Unknown report type: {type}")

    # Enter the account in the search input box
    search_input = WebDriverWait(dr, 20).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                f'input[data-uxi-element-id="selectinput-{account_select_input_id}"]',
            )
        )
    )
    dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
    WebDriverWait(dr, 10).until(
        lambda d: search_input.is_displayed() and search_input.is_enabled()
    )
    dr.execute_script("arguments[0].focus();", search_input)
    search_input.clear()
    print_progress(f"Setting account to {account}")
    search_input.send_keys(account)
    time.sleep(0.5)
    search_input.send_keys(Keys.ENTER)
    time.sleep(SLEEP_AFTER_GRANT)

    search_input = WebDriverWait(dr, 20).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'input[data-uxi-element-id="selectinput-15$142784"]',
            )
        )
    )
    dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
    WebDriverWait(dr, 10).until(
        lambda d: search_input.is_displayed() and search_input.is_enabled()
    )
    dr.execute_script("arguments[0].focus();", search_input)
    search_input.clear()
    print_progress(f"Setting period to {month_year.strftime('%b %Y')}")
    search_input.send_keys(f"{month_year.strftime('%b %Y')}")
    search_input.send_keys(Keys.ENTER)
    time.sleep(SLEEP_AFTER_PERIOD)


def _run_report(dr):
    # Click in the Filter Name box before clicking OK
    try:
        filter_name_input = WebDriverWait(dr, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[data-automation-id="textInputBox"]')
            )
        )
        dr.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", filter_name_input
        )
        filter_name_input.click()
        print_progress("Clicked in the Filter Name input box.")
    except Exception as e:
        print("Could not find or click the Filter Name input box:", e)

    # Now wait for the OK button to be clickable and click it
    try:
        ok_button = WebDriverWait(dr, 20).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'button[data-automation-id="wd-CommandButton_uic_okButton"][title="OK"]',
                )
            )
        )
        dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", ok_button)
        ok_button.click()
        print_progress("OK button to run the report.")
    except Exception as e:
        print("Could not find or click the OK button:", e)


def _load_all_scrollable_rows(dr, scroll_container):
    SCROLL_PAUSE_TIME = 0.5
    SCROLL_INCREMENT = 500  # pixels

    def has_loading_row():
        try:
            dr.find_element(By.CSS_SELECTOR, 'tr[data-testid="loadingRow"]')
            return True
        except:
            return False

    current_position = 0

    while has_loading_row():
        dr.execute_script(
            "arguments[0].scrollTo(0, arguments[1]);",
            scroll_container,
            current_position,
        )
        time.sleep(SCROLL_PAUSE_TIME)
        current_position += SCROLL_INCREMENT


def _set_date_by_label(dr, label_text, month, day, year):
    wait = WebDriverWait(dr, 20)

    # Find the label by its text
    label = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f'//label[@data-automation-id="formLabel" and normalize-space(text())="{label_text}"]',
            )
        )
    )

    # Go up to the enclosing <li> of that label
    ancestor_li = label.find_element(By.XPATH, "./ancestor::li")

    # Find the date wrapper inside that <li>
    date_wrapper = ancestor_li.find_element(
        By.XPATH, './/div[@data-automation-id="dateInputWrapper"]'
    )

    # Now find the inputs inside the wrapper
    month_input = date_wrapper.find_element(
        By.CSS_SELECTOR, 'input[data-automation-id="dateSectionMonth-input"]'
    )
    day_input = date_wrapper.find_element(
        By.CSS_SELECTOR, 'input[data-automation-id="dateSectionDay-input"]'
    )
    year_input = date_wrapper.find_element(
        By.CSS_SELECTOR, 'input[data-automation-id="dateSectionYear-input"]'
    )

    # Clear and set new values
    month_input.clear()
    month_input.send_keys(str(month).zfill(2))

    day_input.clear()
    day_input.send_keys(str(day).zfill(2))

    year_input.clear()
    year_input.send_keys(str(year))


def _goto_finance_reports(dr):
    # Click the global navigation button to open the menu
    global_nav_button = WebDriverWait(dr, 20).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-automation-id="globalNavButton"]')
        )
    )
    global_nav_button.click()
    print_progress("Menu button clicked.")

    # Click the Menu button
    menu_button = WebDriverWait(dr, 5).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-automation-id="globalNavAppsTab"]')
        )
    )
    menu_button.click()
    print_progress("Menu button clicked.")

    # Wait for and click the BYU Finance Dashboard link
    finance_dashboard_link = WebDriverWait(dr, 20).until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                'a[data-automation-id="globalNavAppItemLink"][aria-label="BYU Finance Dashboard"]',
            )
        )
    )
    dr.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", finance_dashboard_link
    )
    WebDriverWait(dr, 5).until(EC.visibility_of(finance_dashboard_link))
    finance_dashboard_link.click()
    print_progress("BYU Finance Dashboard link clicked.")

    # Wait for and click the BYU Finance Reports tab
    tabs = WebDriverWait(dr, 20).until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                'li[data-automation-id="tab"] .gwt-Label[data-automation-id="tabLabel"]',
            )
        )
    )
    found = False
    for tab in tabs:
        if tab.text.strip() == "BYU Finance Reports":
            tab.click()
            print_progress("BYU Finance Reports tab clicked.")
            found = True
            break
    if not found:
        print("Could not find the BYU Finance Reports tab.")
    time.sleep(1)

    # Wait for and click the 'More' button before clicking the report
    try:
        # Wait for the 'More' button to be present in the DOM
        more_button = WebDriverWait(dr, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[data-automation-id="wd-MoreLink"]')
            )
        )
        # Wait until the button is visible (not zero size)
        WebDriverWait(dr, 10).until(
            lambda d: more_button.is_displayed()
            and more_button.size["height"] > 0
            and more_button.size["width"] > 0
        )
        dr.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", more_button
        )
        # Try to click with JS if normal click fails
        try:
            more_button.click()
        except Exception:
            dr.execute_script("arguments[0].click();", more_button)
        print_progress("'More' button clicked.")
    except Exception as e:
        print("Could not find or click the 'More' button:", e)
    time.sleep(1)


def _click_finance_report(dr, report_name):
    """On the 'BYU Finance Reports' page, click the specified report by its name."""
    report_div = WebDriverWait(dr, 5).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"div.WAYC[title='{report_name}']")
        )
    )
    dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", report_div)
    report_div.click()
    print_progress(f"'{report_name}' report clicked.")

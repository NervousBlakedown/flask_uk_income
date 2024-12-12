from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates', static_folder='static')

# Route to test the template rendering
@app.route("/test")
def test():
    return render_template("index.html")

# Create a custom filter for adding thousand separators
@app.template_filter('comma')
def comma_filter(value):
    """Add commas as thousand separators."""
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return value  # Return the value as is if it's not a number

def calculate_tax_and_ni(salary):
    personal_allowance = 12_570
    basic_rate_limit = 37_700
    higher_rate_limit = 125_140

    basic_rate = 0.20
    higher_rate = 0.40
    additional_rate = 0.45

    ni_rate_basic = 0.12
    ni_rate_additional = 0.02

    if salary <= personal_allowance:
        taxable_income = 0
        tax = 0
        basic_band_tax = 0
        higher_band_tax = 0
        additional_band_tax = 0
    elif salary <= basic_rate_limit:
        taxable_income = salary - personal_allowance
        basic_band_tax = taxable_income * basic_rate
        higher_band_tax = 0
        additional_band_tax = 0
    elif salary <= higher_rate_limit:
        taxable_income = salary - personal_allowance
        basic_band_tax = (basic_rate_limit - personal_allowance) * basic_rate
        higher_band_tax = (salary - basic_rate_limit) * higher_rate
        additional_band_tax = 0
    else:
        taxable_income = salary - personal_allowance
        basic_band_tax = (basic_rate_limit - personal_allowance) * basic_rate
        higher_band_tax = (higher_rate_limit - basic_rate_limit) * higher_rate
        additional_band_tax = (salary - higher_rate_limit) * additional_rate

    tax = basic_band_tax + higher_band_tax + additional_band_tax

    if salary <= personal_allowance:
        ni = 0
    elif salary <= basic_rate_limit:
        ni = (salary - personal_allowance) * ni_rate_basic
    else:
        ni = (basic_rate_limit - personal_allowance) * ni_rate_basic + (salary - basic_rate_limit) * ni_rate_additional

    return tax, ni

def calculate_net_income(salary):
    tax, ni = calculate_tax_and_ni(salary)
    net_income = salary - tax - ni
    return net_income

def rent_budget(net_income, percentages=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50]):
    monthly_net_income = net_income / 12
    budgets = {}
    for percentage in percentages:
        budgets[f'{percentage}%'] = monthly_net_income * (percentage / 100)
    return budgets

@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize variables in case of GET request
    salary = None
    tax = None
    ni = None
    net_income = None
    net_income_monthly = None
    rent_budgets = {}

    if request.method == "POST":
        try:
            salary = float(request.form["salary"])
        except ValueError:
            return render_template("index.html", error="Please enter a valid salary.")
        
        # Calculate tax, NI, and net income
        tax, ni = calculate_tax_and_ni(salary)
        net_income = calculate_net_income(salary)
        net_income_monthly = net_income / 12

        # Calculate rent budgets based on percentages
        rent_budgets = rent_budget(net_income)
        
    # Pass the variables to the template (with rent_budgets initialized)
    return render_template(
        "index.html",
        salary=salary,
        tax=tax,
        ni=ni,
        net_income=net_income,
        net_income_monthly=net_income_monthly,
        rent_budgets=rent_budgets
    )


if __name__ == "__main__":
    app.run(debug=True)

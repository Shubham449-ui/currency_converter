from flask import Flask, request, render_template
import requests

app = Flask(__name__)

# FastForex API key and URL
API_KEY = "14d1785410-a30deca493-szi22j"
API_URL = "https://api.fastforex.io/fetch-all?from={}&api_key={}"
HEADERS = {"accept": "application/json"}

# Fetch all available currencies from the API
def get_all_currencies():
    try:
        response = requests.get(API_URL.format("USD", API_KEY), headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                return sorted(data["results"].keys())
            return ["USD", "EUR"]  # Fallback in case of unexpected API response
        return ["USD", "EUR"]  # Fallback in case of API failure
    except Exception as e:
        print(f"Error fetching currencies: {e}")
        return ["USD", "EUR"]  # Fallback in case of any error

CURRENCIES = get_all_currencies()

@app.route("/", methods=["GET", "POST"])
def currency_converter():
    result = None
    amount = 1.0
    from_currency = "USD"
    to_currency = "EUR"

    if request.method == "POST":
        try:
            amount = float(request.form.get("amount"))
            from_currency = request.form.get("from_currency")
            to_currency = request.form.get("to_currency")

            # Fetch exchange rates for the selected base currency
            response = requests.get(API_URL.format(from_currency, API_KEY), headers=HEADERS)
            data = response.json()

            if response.status_code == 200 and "results" in data:
                rate = data["results"][to_currency]
                converted_amount = amount * rate
                result = f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}"
            else:
                result = "Error fetching exchange rates. Please try again."
        except ValueError:
            result = "Invalid input. Please enter a valid number."
        except KeyError:
            result = "Currency not supported or API error."
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template("index.html", currencies=CURRENCIES, result=result,
                         amount=amount, from_currency=from_currency, to_currency=to_currency)

if __name__ == "__main__":
    app.run(debug=True)
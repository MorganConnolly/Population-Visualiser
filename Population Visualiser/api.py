from flask import Flask, render_template, request, send_file, session
from flask_session import Session
import requests # REST API interaction
import matplotlib
matplotlib.use('Agg') # Use the Agg backend to avoid GUI issues.
import matplotlib.pyplot as plt

app = Flask(__name__) 

# Setup sessions.
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Pages
@app.route("/", methods = ["GET", "POST"])
def menu_page():
    return render_template("menu.html")

@app.route("/world_breakdown", methods = ["GET", "POST"])
def world_breakdown_page():
    # Get countries for dropdown.
    countries_and_populations = requests.get("https://countriesnow.space/api/v0.1/countries/population").json()
    countries = [dataset['country'] for dataset in countries_and_populations['data'][46:]]                         # Countries appear after index 45.
    populations = [dataset['populationCounts'][-1]['value'] for dataset in countries_and_populations['data'][46:]] # Retrieves most recent population recordings.

    # Get countries picked to keep population log updated.
    country_names_picked = session.get("country_names_picked", [])
    country_populations_picked = session.get("country_populations_picked", [])

    if request.method == "POST":
        # If country added to graph, append name and population to session variable.
        if "submit" in request.form:
            country_name = request.form["country"]

            # Prevents the same country from being added twice.
            if country_name not in country_names_picked:
                country_population = int(populations[countries.index(country_name)])
                
                country_names_picked.append(country_name)
                country_populations_picked.append(country_population)

                session["country_names_picked"] = country_names_picked
                session["country_populations_picked"] = country_populations_picked
        
        # If reset button pressed, clear session data and display new graph.
        else:
            session["country_names_picked"] = []
            session["country_populations_picked"] = []

            return render_template("world_breakdown.html", countries=countries, countries_picked=[])

    return render_template("world_breakdown.html", countries=countries, countries_picked=list(zip(country_names_picked, country_populations_picked)))

@app.route("/country_breakdown", methods = ["GET", "POST"])
def country_breakdown_page():
    # Get countries for dropdown.
    cities_and_populations = requests.get("https://countriesnow.space/api/v0.1/countries/population/cities").json()
    countries = []
    cities = []
    for dataset in cities_and_populations['data']:
        if dataset['country'] not in countries:
            countries.append(dataset['country'])
    countries = countries[:208]                    # Rogue values removed.

    # Get city picked data to keep population log updated.
    city_names_picked = session.get("city_names_picked", [])
    city_populations_picked = session.get("city_populations_picked", [])

    if request.method == "POST":
        # If country selected, get & display city options and add to session data for retrieval when adding a city.
        if "submit_country" in request.form:
            country_name = request.form['country']
            cities = [dataset['city'] for dataset in cities_and_populations['data'] if dataset['country'] == country_name]
            session["country_name_picked"] = country_name
        
        # If city added to graph, get population, add to session data and generate graph.
        elif "submit_city" in request.form:
            try:                                 # If no country has been selected, it will throw an error.
                city_name = request.form['city']

                # Prevents the same city from being added twice.
                if city_name not in city_names_picked:  

                    city_names_picked.append(city_name)
                    for dataset in cities_and_populations['data']:
                        if dataset['city'] == city_name:
                            city_populations_picked.append(int(dataset['populationCounts'][-1]['value'])) # Retrieves most recent population recordings.

                    session["city_names_picked"] = city_names_picked
                    session["city_populations_picked"] = city_populations_picked

                # Re-retrieve city list using country name.
                country_name_picked = session.get("country_name_picked", [])
                cities = [dataset['city'] for dataset in cities_and_populations['data'] if dataset['country'] == country_name_picked]

            except Exception as error:
                print(f"Error: {error}")

        else:
            session["city_names_picked"] = []
            session["city_populations_picked"] = []

            return render_template("country_breakdown.html", countries=countries, cities=cities, cities_picked=[])

    return render_template("country_breakdown.html", countries=countries, cities=cities, cities_picked=list(zip(city_names_picked, city_populations_picked)))

# Graphs 
@app.route("/world_breakdown_graph")
def world_breakdown_graph():
    file_path = "static/population_by_country.png"

    # Creates variables if they don't exist.
    country_names_picked = session.get("country_names_picked", [])
    country_populations_picked = session.get("country_populations_picked", [])

    # Create graph.
    try:
        plt.bar(country_names_picked, country_populations_picked)
        plt.xlabel("Country")
        plt.xticks(rotation = 90)
        plt.ylabel("Population")
        plt.ylim(0)
        plt.tight_layout()     # Prevents overlapping.
        plt.savefig(file_path) # Replaces existing graph.
        plt.close()
    except Exception as error:
        print(f"Error: {error}")
    
    return send_file(file_path, mimetype = 'image/png')

@app.route("/country_breakdown_graph")
def country_breakdown_graph():
    file_path = "static/population_by_city.png"

    # Creates variables if they don't exist.
    city_names_picked = session.get("city_names_picked", [])
    city_populations_picked = session.get("city_populations_picked", [])

    # Create graph.
    try:
        plt.bar(city_names_picked, city_populations_picked)
        plt.xlabel("City")
        plt.xticks(rotation = 90)
        plt.ylabel("Population")
        plt.ylim(0)
        plt.tight_layout()     # Prevents overlapping.
        plt.savefig(file_path) # Replaces existing graph.
        plt.close()
    except Exception as error:
        print(f"Error: {error}")
    
    return send_file(file_path, mimetype = 'image/png')

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = "8080", debug = False)
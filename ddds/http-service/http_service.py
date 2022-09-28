# -*- coding: utf-8 -*-

import json

import requests

from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)
environment = Environment()
API_KEY = "acf1ca3d5daa73b0ff54ab8be72f9c1b"


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def get_current_data(city, country, unit="metric"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&units={unit}&appid={API_KEY}"
    print(url)
    response = requests.get(url)
    data = response.json()
    return data

@app.route("/get_temperature", methods=['POST'])
def get_temperature():
    payload = request.get_json()
    city = payload["context"]["facts"]["city_to_search"]["grammar_entry"]
    country = payload["context"]["facts"]["country_to_search"]["grammar_entry"]
    
    api_response = get_current_data(city, country)
    temperature = str(api_response['main']['temp'])
    return query_response(value=temperature, grammar_entry=None)

@app.route("/get_weather", methods=['POST'])
def get_weather():
    payload = request.get_json()
    city = payload["context"]["facts"]["city_to_search"]["grammar_entry"]
    country = payload["context"]["facts"]["country_to_search"]["grammar_entry"]
    
    api_response = get_current_data(city, country)
    weather = str(api_response['main']['description'])
    return query_response(value=weather, grammar_entry=None)



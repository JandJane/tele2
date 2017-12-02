# -*- coding: utf-8 -*-
import requests

from flask import Flask
from flask import request
from flask import make_response

import apiai

import json
import os

import utils

headers = {'Content-type': 'application/json',
           'Accept': 'application/json',
           'Content-Encoding': 'utf-8',
           'X-API-Token': 'as20df'}
url = 'http://tele2-hackday-2017.herokuapp.com/api/'

CLIENT_ACCESS_TOKEN = 'efaf1fa97c27480e85b34792748cb8d5'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    print('webhook')
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "AskPhoneNumber":
        result = req.get("result")
        parameters = result.get("parameters")
        phone = parameters.get("phone-number")
        print(req['originalRequest']['data']['message']['text'])
        if utils.phone_standard(phone):
            speech = "Спасибо, ваш номер " + utils.phone_standard(phone) + " успешно сохранён."
            # post this phone number
        else:
            speech = "Неверный формат ввода. \nПожалуйста, введите номер в формате 79XXXXXXXXX"
            # delete phone entity
    elif req.get("result").get("action") == "GetTariff":
        speech = GetTariff(req)
        return speech
    elif req.get("result").get("action") == "ShowSlugs":
        speech = ShowSlugs(req)
        return speech
    elif req.get("result").get("action") == "AvailableTariffs":
        speech = AvailableTariffs(req)
        return speech
    elif req.get("result").get("action") == "MySlugs":
        speech = MySlugs(req)
        return speech
    elif req.get("result").get("action") == "Balance":
        speech = Balance(req)
        return speech             
    
    print("Response: " + speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "AskPhoneNumber"
    }


def AvailableTariffs(req):
    url = 'http://tele2-hackday-2017.herokuapp.com/api/tariffs/available'
    
    response = requests.get(url, headers=headers)

    response = response.json()['data']
    speech = ''
    for i in range(len(response)):
        speech += "Тариф - **" + response[i]["name"] + "**\n"
    
        speech += "Абонентская плата = **" + str(response[i]["subscriptionFee"] // 100)
    
        speech += "** __руб.__  **" + str(response[i]["subscriptionFee"] % 100)
    
        speech += "** __коп.__ \n"
    
        speech += "Подробную информацию смотрите здесь: " + response[i]["url"] + "\n"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "AvailableTariffs"
    }
        

def GetTariff(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    try:
               number = parameters.get("phone-number")

               headers = {'Content-type': 'application/json',
                          'Accept': 'application/json',
                          'Content-Encoding': 'utf-8',
                          'X-API-Token': 'string'}
               url = 'http://tele2-hackday-2017.herokuapp.com/api/subscribers/' + number + '/tariff'
               response = requests.get(url, headers=headers)
               response = response.json()['data']

               speech = "Ваш тариф - **" + response["name"] + "**\n"
               speech += "Абонентская плата = **" + str(response["subscriptionFee"] // 100)
               speech += "** __руб.__  **" + str(response["subscriptionFee"] % 100)
               speech += "** __коп.__ \n"
               speech += "Подробную информацию смотрите здесь: " + response["url"]
    except Exception:
           speech = "Cначала введите номер телефона"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "GetTariff"
    }


def ShowSlugs(req):
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8'}
    url = "http://tele2-hackday-2017.herokuapp.com/api/services/available"
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    if len(response) > 0:
        speech = "Список услуг:\n\n"
        for i in range(len(response)):
            speech += response[i]["name"] + '\n'
            speech += response[i]["description"] + '\n'
            if response[i]["connectionFee"] == 0:
                speech += "Подключение бесплатно\n"
            else:
                speech += "Стоимость подключения: " + str(response[i]["connectionFee"] // 100) + " руб. " + str(response[i]["connectionFee"] % 100) + " коп.\n"
            if response[i]["subscriptionFee"] == 0:
                speech += "Без абонентской платы\n"
            else:
                speech += "Абонентская плата: " + str(response[i]["subscriptionFee"] // 100) + " руб. " + str(response[i]["subscriptionFee"] % 100) + " коп.\n"
            speech += "Чтобы подключить услугу, введите: Подключить " + response[i]["slug"] + '\n\n'
    else:
        speech = "ERROR"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "ShowSlugs"
    }


def MySlugs(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    number = parameters.get("phone-number")
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    url = "http://tele2-hackday-2017.herokuapp.com/api/subscribers/" + number + "/services"
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    if len(response) > 0:
        speech = "Список услуг:\n\n"
        for i in range(len(response)):
            speech += response[i]["name"] + '\n'
            speech += response[i]["description"] + '\n'
            if response[i]["connectionFee"] == 0:
                speech += "Подключение бесплатно\n"
            else:
                speech += "Стоимость подключения: " + str(response[i]["connectionFee"] // 100) + " руб. " + str(
                    response[i]["connectionFee"] % 100) + " коп.\n"
            if response[i]["subscriptionFee"] == 0:
                speech += "Без абонентской платы\n"
            else:
                speech += "Абонентская плата: " + str(response[i]["subscriptionFee"] // 100) + " руб. " + str(
                    response[i]["subscriptionFee"] % 100) + " коп.\n"
            speech += "Чтобы отключить услугу, введите: Отключить " + response[i]["slug"] + '\n\n'
    else:
        speech = "ERROR"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "MySlugs"
    }


def Balance(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    number = parameters.get("phone-number")
    headers = {'Content-type': 'application/json',
                  'Accept': 'application/json',
                  'Content-Encoding': 'utf-8',
                  'X-API-Token': 'string'}    
    url = 'http://tele2-hackday-2017.herokuapp.com/api/subscribers/' + number + '/balance'
    response = requests.get(url, headers = headers)
    response = response.json()['data']
    speech = "Остаток интернета: " + str(response['internet']//1024) + "Гб" + str(response['internet']%1024) + "Мб\n"
    speech += "Остаток СМС: " + str(response['sms']) + '\n'
    speech += "Остаток минут: " + str(response['call']//60) + '\n'
    speech += "Текущий баланс: " + str(response['money']//100) + 'Руб.' + str(response['money'] % 100) + 'Коп.\n'
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "Balance"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(1)
    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

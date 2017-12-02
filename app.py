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
    elif req.get("result").get("action") == "UserData":
        speech = UserData(req)
        return speech
    elif req.get("result").get("action") == "SwitchSlug":
        speech = SwitchSlug(req)
        return speech
    elif req.get("result").get("action") == "SwitchOffSlug":
        speech = SwitchOffSlug(req)
        return speech
    elif req.get("result").get("action") == "SlugDescription":
        speech = SlugDescription(req)
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
        speech += "Тариф - " + response[i]["name"] + "\n"

        speech += "Абонентская плата = " + str(response[i]["subscriptionFee"] // 100)

        speech += " руб.  " + str(response[i]["subscriptionFee"] % 100)

        speech += " коп. \n"

        speech += "Чтобы подключить тариф, введите: Подключить " + response[i]["slug"] + '\n'

        speech += "Подробную информацию смотрите здесь: " + response[i]["url"] + "\n\n"
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
        speech = "Ваш тариф - " + response["name"] + "\n"
        speech += "Абонентская плата = " + str(response["subscriptionFee"] // 100)
        speech += " руб.  " + str(response["subscriptionFee"] % 100)
        speech += " коп. \n"
        speech += "Подробную информацию смотрите здесь: " + response["url"]
    except Exception:
        speech = "Номер телефона неверный"
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
    if response:
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
            speech += "Чтобы подключить услугу, введите: Подключить " + response[i]["slug"] + '\n'
            speech += "Подробнее об услуге: " + response[i]["url"] + '\n\n'
    else:
        speech = "Что-то пошло не так."
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "ShowSlugs"
    }


def MySlugs(req):
    result = req.get("result").get('contexts')[0]
    print(result)
    print(req)
    parameters = result.get("parameters")
    number = parameters.get("phone-number")
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    url = "http://tele2-hackday-2017.herokuapp.com/api/subscribers/" + number + "/services"
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    if response:
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
            speech += "Чтобы отключить услугу, введите: Отключить " + response[i]["slug"] + '\n'
            speech += "Подробнее об услуге: " + response[i]["url"] + '\n\n'

    else:
        speech = "Номер телефона неверный."

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
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    if response:
        speech = "Остаток интернета: " + str(response['internet'] // 1024) + "Гб" + str(
            response['internet'] % 1024) + "Мб\n"
        speech += "Остаток СМС: " + str(response['sms']) + '\n'
        speech += "Остаток минут: " + str(response['call'] // 60) + '\n'
        speech += "Текущий баланс: " + str(response['money'] // 100) + ' Руб.' + str(response['money'] % 100) + ' Коп.\n'
    else:
        speech = "Номер телефона неверный"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "Balance"
    }


def UserData(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    number = parameters.get("phone-number")

    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    url = 'http://tele2-hackday-2017.herokuapp.com/api/subscribers/' + number
    response = requests.get(url, headers=headers)
    response = response.json()['data']
    if response:
        speech = "Телефон " + response["msisdn"] + "\n"
        speech += "ФИО " + response["lastName"] + ' ' + response["firstName"] + ' ' + response["middleName"] + '\n'
        speech += "email адрес " + response["email"]
    else:
        speech = "Номер телефона неверный\n"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "UserData"
    }


def SwitchSlug(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    number = parameters.get("phone-number")
    slug = parameters.get("slug-name")
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    try:
        url = 'http://tele2-hackday-2017.herokuapp.com/api/subscribers/' + number + '/services/' + slug
        response = requests.put(url, headers=headers)
        response = response.json()['data']
        if response.get('status').get('code') == 200:
            speech = "Услуга успешно подключена!"
        else:
            speech = "Ошибка при подключении услуги"
    except Exception:
        speech = "Ошибка при подключении услуги"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "SwitchSlug"
    }


def SwitchOffSlug(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    number = parameters.get("phone-number")
    slug = parameters.get("slug-name")
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    try:
        url = 'http://tele2-hackday-2017.herokuapp.com/api/subscribers/' + number + '/services/' + slug
        response = requests.delete(url, headers=headers)
        response = response.json()['data']
        if response.get('status').get('code') == 200:
            speech = "Услуга успешно отключена"
        else:
            speech = "Ошибка при отключении услуги"
    except Exception:
        speech = "Ошибка при отключении услуги"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "SwitchOffSlug"
    }


def SlugDescription(req):
    result = req.get("result").get('contexts')[0]
    parameters = result.get("parameters")
    slug = parameters.get("slug-name")

    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8',
               'X-API-Token': 'string'}
    k = 0
    headers1 = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'Content-Encoding': 'utf-8'}
    url1 = "http://tele2-hackday-2017.herokuapp.com/api/services/available"
    response = requests.get(url1, headers=headers1)
    response = response.json()['data']
    for i in response:
        if i["slug"] == slug:
            k = 1
    if k == 1:
        url = "http://tele2-hackday-2017.herokuapp.com/api/services/" + slug
        response = requests.get(url, headers=headers)
        response = response.json()['data']
        speech = response["name"] + '\n'
        speech += response["description"] + '\n'
        if response["connectionFee"] == 0:
            speech += "Подключение бесплатно\n"
        else:
            speech += "Стоимость подключения: " + str(response["connectionFee"] // 100) + " руб. " + str(
                response["connectionFee"] % 100) + " коп.\n"
        if response["subscriptionFee"] == 0:
            speech += "Без абонентской платы\n"
        else:
            speech += "Абонентская плата: " + str(response["subscriptionFee"] // 100) + " руб. " + str(
                response["subscriptionFee"] % 100) + " коп.\n"
        speech += "Чтобы подключить услугу, введите: Подключить " + response["slug"] + '\n'
        speech += "Подробнее об услуге: " + response["url"] + '\n\n'
    else:
        speech = "Такой услуги не существует\n"
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "SlugDescription"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(1)
    print("Starting app on port %d" % port)

app.run(debug=False, port=port, host='0.0.0.0')

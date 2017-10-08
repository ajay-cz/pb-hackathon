# -*- coding: utf-8 -*-
import os
import json
import math
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from app.integrations import state_province
from app.integrations.channels import sync_orders
from app.integrations.channels.woo_commerce import WoocommerceOrders
from app.integrations.channels.prestashop import PrestashopOrders
from app.integrations.chatbot.ecourierz import track_order, Bot
from app.integrations.shippers.pb import fetch_shipping_rates, create_shipment
from app.utils import BaseDataTables, asbool
from app.integrations.duty_calculator import *
from app.integrations.duty_calculator.duty_calculator import dutycalculator
from app.libs.pbshipping.tutorial_rest import *
import textwrap

dev = 'True' == os.environ.get('isDev', 'True')
# configuration
if dev:
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_NAME = 'pb'
else:
    MONGODB_HOST = 'mongodb://heroku_b5gwlnj9:j7ljghvja42auraev21ngaghon@ds159254.mlab.com:59254/heroku_b5gwlnj9'
    MONGODB_PORT = 59254
    MONGODB_NAME = 'heroku_b5gwlnj9'

# DB Defaults
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = connection[MONGODB_NAME]

# Flask app
app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True
app.jinja_env.add_extension('jinja2.ext.do')

INIT_PAGE = 0
PAGE_LIMIT = 25


@app.route('/')
def home_page():
    """
    View Controller for the Home Page
    :return:
    """
    return render_template('home.html', store_settings=list(db.store_settings.find()) or [])


# <--- Start Settings Page
@app.route('/settings')
def settings_page():
    """
    View Controller for the Settings Page
    :return:
    """
    return render_template('settings.html')


@app.route('/settings/shipper-settings', methods=['GET', 'POST'])
def shipper_settings_page():
    """
    View Controller for the Shippers' Settings Page
    eg., Settings page for configuring PB Keys, ECZ Keys etc

    :return:
    """
    return render_template('shipper_settings.html')


@app.route('/settings/warehouse-settings', methods=['GET', 'POST'])
def warehouse_settings_page():
    my_dict2 = {y: x for x, y in state_province.iteritems()}
    if request.method == 'POST':
        form_data = {}
        for i in request.form.items():
            form_data.update({i[0]: i[1]})
            if i[0] == 'addressLines':
                lines = textwrap.wrap(i[1], 60, break_long_words=False)
                form_data.update({'addressLines': lines})
            form_data.update({'countryCode':'US'})
        try:
            store_order = {'_id': 'wh_1'}
            fromAddress = {'fromAddress': form_data}
            i = db.warehouse_settings.update_one(store_order, {'$set': fromAddress}, upsert=True)
        except:
            print('Please check the data')
            pass
    warehouse_settings = list(db.warehouse_settings.find()) or [{}]

    return render_template('warehouse-settings.html', warehouse_settings=warehouse_settings,
                           state_province=sorted(state_province.items()))


@app.route('/settings/erpnext-settings', methods=['GET', 'POST'])
def erpnext_settings_page():
    """ erpnext_settings_page

    :return:
    """
    return render_template('erpnext_settings.html')


@app.route('/settings/channel-settings', methods=['GET', 'POST'])
def channel_settings_page():
    """
    View Controller for the Channels' Settings Page
    :return:
    """
    store_order = None
    if request.method == 'POST':
        form_data = {}
        for i in request.form.items():
            if i[0] == 'store_order':
                store_order = {'_id': i[1]}
            else:
                form_data.update({i[0]: i[1]})
        try:
            i = db.store_settings.update_one(store_order, {
                '$set': form_data}, upsert=True)
        except:
            print('Please check the data')
            pass

    return render_template('channel_settings.html', store_settings=db.store_settings.find())


# End Settings Page  --->

@app.route('/sync-orders', methods=['GET', 'POST'])
def sync_store_orders():
    """
    Sync Orders From Sales channel
    :return:
    """
    if not db.warehouse_settings.find_one():
        return redirect(url_for('warehouse_settings_page'))
    if not db.store_settings.find_one():
        return redirect(url_for('channel_settings_page'))
    error_list = []
    if request.method == 'POST':
        print(request.form.items())
        try:
            sync_orders(db, [s_type[0] for s_type in request.form.items() if asbool(s_type[1])])
        except Exception, e:
            error_list.append(str(e.message))

    return render_template('dashboard.html', columns=columns, error=error_list)


@app.route('/accounting', methods=['GET', 'POST'])
def accounting_page():
    """

    :return:
    """
    return render_template('accounting.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard_page():
    """

    :return:
    """
    return render_template('dashboard.html', columns=columns)


# TODO: Add the fields as required
columns = ['Store Type', 'Order ID', 'Created on and Value', 'Billing Details', 'Shipping Details', 'Shipping Info']


@app.route('/_server_data')
def get_server_data():
    """

    :return:
    """
    # dummy data. to be replaced with data from synced db
    # columns='<table><thead><tr><th>Order ID</th><th>Created on and Value</th><th>Billing Details</th><th>Shipping Details</th><th>Dimensions And Weight</th></tr><thead></table>'
    orders = db.order_data.find({})
    # TODO: Modify the below fields to make them in sync with the required columns.
    # TODO (cont) eg., The Senders Address need not be displayed on the datatable
    collection = [dict(zip(
        columns,
        [
            order.get('store_type'),
            '<div id="order_info" data-order=\'%s\'>%s</div>' % (json.dumps(order), str(order.get('order_id'))),
            '<tr><td>' + order.get('order_created') + '<br>' + str(order.get('product_value')) + ' INR</td>',
            '<td>' + order.get('fromAddress', {}).get('name') + '<br>' + order.get('fromAddress', {}).get(
                'postalCode') + '</td>',
            '<td>' + order.get('toAddress', {}).get('name') + '<br>' + order.get('toAddress', {}).get(
                'postalCode') + '</td>',
            '<span id="rates"></span><br><span id="duties"></span><br>'
            '<span id="shipment">Tracking: <b>%s</b> <br> <a id="downloadLink" class="%s" href="%s" target="_blank" type="application/octet-stream" download="%s.pdf" class="has-ripple">Download Label</a></span>' %
            (
                order.get('pb_info', {}).get('tracking_number', ''),
                'hide' if not order.get('pb_info', {}).get('tracking_number') else '',
                order.get('pb_info', {}).get('label', ''),
                order.get('pb_info', {}).get('tracking_number', '')
            )

        ]
    )) for order in orders]

    # request -> Flask Request Object
    # @Rohit, check BaseDataTabAles class to understand the arguments. u can pass the results from the DB as well.
    # check class for info
    results = BaseDataTables(request, columns, collection).output_result()
    # print(json.dumps(results))
    # return the results in json for the datatable
    return json.dumps(results)


@app.route('/trackbot', methods=['GET', 'POST'])
def track_bot_hook():
    """

    :return:
    """
    print(request.get_json())

@app.route('/duty', methods=['POST'])
def duty_calculator():
    """

    :return:
    """
    duty_info=request.get_json()
    print duty_info
    sender_country=str(COUNTRY_MAP_3_ISO.get(duty_info.get('fromAddress',{}).get('countryCode')))
    receiver_country=str(COUNTRY_MAP_3_ISO.get(duty_info.get('toAddress',{}).get('countryCode')))
    content=str(duty_info.get('content'))
    duty=dutycalculator(sender_country.lower(),receiver_country.lower(),content)
    duty_res=duty.dutycalculate()
    sales_tax=duty_res.get('sales_tax') or 0
    tax_break=duty_res.get('tax_break',{}) or 0
    for i,j in tax_break.iteritems():
        j+=str(j)
    final_tax='sales_tax('+str(sales_tax)+') +'+j
    return final_tax

@app.route('/create-shipment', methods=['POST'])
def create_shipping_label():
    """

    :return:
    """
    order_info = request.get_json()
    my_parcel = order_info.get('parcel')
    origin_address = order_info.get('fromAddress')
    dest_address = order_info.get('toAddress')

    authenticate_and_authorize('fbtgdPwCsZqXGPtuK8q4339O9CeSuAim', 'XNImibJsDG1D4GWk')

    shipment = create_shipment(parcel_info=my_parcel, origin_addr=origin_address, dest_addr=dest_address)

    order_update = db.order_data.find_one({'_id': str(order_info.get('_id'))})

    if order_update:
        order_update['pb_info'] = shipment
        db.order_data.save(order_update)

    return json.dumps({"redirect_to": url_for('sync_store_orders'), "shipment": shipment})
    # order['pb_info'] {
    # "tracking_number" : "9405509898642004077115",
    # "label" : "https://web-prt3.gcs.pitneybowes.com/usps/325584758/outbound/label/d469a1db4f2b4d4c862fc2d43cb3267e.pdf"
    # }

@app.route('/send-message', methods=['POST'])
def send_message():
    """

    :return:
    """
    chat_message = request.form.get('message')
    bot = Bot(1)
    data = bot.chat(chat_message)
    order_id = bot.Track(data)
    track_response = track_order(str(order_id))

    return json.dumps(track_response)


@app.route('/remove-orders')
def delete_all_synced_orders():
    """

    :return:
    """
    db.order_data.remove({})

    return redirect('/dashboard')


if __name__ == '__main__':
    order_update = db.order_data.find_one({'_id': str(u'd2134a5a-fccd-45c0-aafd-ecf05efc0609')})
    print(order_update)
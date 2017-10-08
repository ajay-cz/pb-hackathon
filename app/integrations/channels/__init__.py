# -*- coding: utf-8 -*-
import threading

from app.integrations.channels.prestashop import PrestashopOrders
from app.integrations.channels.woo_commerce import WoocommerceOrders
from flask import redirect

WOOCOMMERCE = 'woocommerce'
PRESTASHOP = 'prestashop'


def fetch_store_settings(db):
    db.store_settings.find()


def sync_orders(db, store_types=None):
    """

    :param store_type:
    :return:
    """
    if store_types:
        stores_info = [db.store_settings.find_one({'store_type': {'$in': store_types}})]
    else:
        stores_info = db.store_settings.find()

    if not stores_info:
        return redirect('/settings', code=302)

    _thread_list = []
    for settings in stores_info:
        if settings.get('store_type', '').lower() == WOOCOMMERCE:
            store_url = settings.get('store_url')
            consumer_key = settings.get('consumer_key')
            consumer_secret = settings.get('consumer_secret')
            w = WoocommerceOrders(store_url, consumer_key, consumer_secret)
            _thread_list.append(threading.Thread(name='WoocommerceOrders', target=w.sync_orders, args=(db,)))

        if settings.get('store_type', '').lower() == PRESTASHOP:
            store_url = settings.get('store_url')
            consumer_key = settings.get('consumer_key')
            p = PrestashopOrders(store_url, consumer_key)
            _thread_list.append(threading.Thread(name='PrestashopOrders', target=p.sync_orders, args=(db,)))

    for _t in _thread_list:
        _t.start()

    for x in _thread_list:
        x.join()

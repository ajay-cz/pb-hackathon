import json
import os
import uuid
import math
from woocommerce import API
from pymongo import MongoClient

sample_consumer_key = 'ck_cd992dd7eab3b057a6b49de75dc6dd68b6fd39ed'
sample_consumer_secret = 'cs_66e0adc9c5348857216561d2384c6dfa5f81a3ee'
sample_store_url = 'http://base1.mynatcom.in'


# Consumer key -  ck_cd992dd7eab3b057a6b49de75dc6dd68b6fd39ed
#
# Consumer Secret -  cs_66e0adc9c5348857216561d2384c6dfa5f81a3ee
#
# http://base1.mynatcom.in/

class WoocommerceOrders:
    """

    """

    def __init__(self, store_url, consumer_key, consumer_secret):
        """

        :param store_url:
        :param consumer_key:
        :param consumer_secret:
        """
        self.__wcapi = API(
            url=store_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            # wp_api=True,
            # version="wc/v1",
            timeout=15
        )

    def add_order(self, data):
        print(self.__wcapi.post("orders", data).json())

    def fetch_all_orders(self):
        """

        :return:
        """
        orders_list = self.__wcapi.get("orders").json()
        if orders_list and 'orders' in orders_list:
            return orders_list['orders']
        return []

    def fetch_pending_processing_orders(self):
        """

        :return:
        """
        orders_list = self.__wcapi.get('orders?status=processing').json()
        if orders_list and 'orders' in orders_list:
            return orders_list.get('orders', [])
        return []

    def fetch_product_details(self, product_id):
        """

        :param product_id:
        :return:
        """
        if product_id:
            return self.__wcapi.get("products/%s" % product_id).json()

        return {}

    def update_order_status(self, order_id, status, order_note):
        """

        :param status:
        :return:
        """
        # #print order_id
        if order_id and status:
            data = {
                "order": {
                    "status": status,
                    "order_note": order_note,
                    "note": order_note
                }
            }
            r = self.__wcapi.put("orders/%s" % order_id, data).json()
            # #print r
            return r

        return {}

    def update_order_notes(self, order_id, note, notify_consumer=False):
        """

        :param order_id:
        :param notes:
        :return:
        """
        # #print order_id
        if order_id and note:
            data = {
                "order_note": {
                    "note": note,
                    "order_note": note,
                    "customer_note": notify_consumer
                }
            }
            r = self.__wcapi.post("orders/%s/notes" % order_id, data).json()
            # #print r
            return r

        return {}

    def sync_orders(self, db):
        """

        :return:
        """
        orders_list = self.fetch_all_orders()
        fromAddress = list(db.warehouse_settings.find()) or []
        for i in orders_list:
            # print(i)
            shipping_addr = i.get("customer", "").get("shipping_address", {})
            billing_addr = i.get("customer", "").get("billing_address", {})
            order_created = i.get('updated_at', '')
            print('%s-%s' % (i.get('id') ,str(shipping_addr.get("country", billing_addr.get('country', 'US')))))
            toAddress = {
                "company": str(shipping_addr.get("company", billing_addr.get('company', ''))),
                "name": str(shipping_addr.get("first_name", billing_addr.get('first_name', ''))) + str(shipping_addr.get("last_name", billing_addr.get('last_name', ''))),
                "phone": str(shipping_addr.get("phone", billing_addr.get('phone', ''))),
                "email": str(shipping_addr.get("email", billing_addr.get('email', ''))),
                "residential": True,
                "addressLines": [
                    str(shipping_addr.get("address_1", billing_addr.get('address_1', ''))),
                    str(shipping_addr.get("address_2", billing_addr.get('address_2', '')))
                ],
                "cityTown": str(shipping_addr.get("city", billing_addr.get('city'))),
                # "stateProvince": '',
                "postalCode": str(shipping_addr.get("postcode", billing_addr.get('postcode', ''))),
                "countryCode": str(shipping_addr.get("country", billing_addr.get('country', 'US'))),
                # "status": "NOT_CHANGED"
            }
            line_items = i.get('line_items', [])
            parcel = {}
            product_value = 0
            content = ''
            for line_item in line_items:
                product_id = line_item.get('product_id')
                product_det = self.fetch_product_details(product_id)
                dimensions = product_det.get('product', {}).get('dimensions')
                length = 0.0
                width = 0.0
                height = 0.0
                weight = 0.0
                irregularParcelGirth = 0.0
                product_value = (int(product_det.get('product', {}).get('regular_price') or 0))
                length = int(math.ceil(int(dimensions.get('length', '10') or 10.0) * float(0.34)))
                width = int(math.ceil(int(dimensions.get('width', '10') or 10.0) * float(0.34)))
                height = int(math.ceil(int(dimensions.get('height', '10') or 10.0) * float(0.34)))
                irregularParcelGirth = int(round(int(length * width * height) / float(3000)))
                weight = int(math.ceil(int(product_det.get('product', {}).get('weight', '100') or 100.0) * float(0.0353)))
                content = line_item.get('name')
                parcel = {
                    "weight": {
                        "unitOfMeasurement": "OZ",
                        "weight": weight
                    },
                    "dimension": {
                        "unitOfMeasurement": "IN",
                        "length": length,
                        "width": width,
                        "height": height,
                        "irregularParcelGirth": irregularParcelGirth
                    }
                }

            order_details = {
                "order_created": order_created,
                "fromAddress": fromAddress[0].get('fromAddress'),
                "toAddress": toAddress,
                "parcel": parcel or {},
                "store_type": "Woocommerce",
                "product_value": product_value,
                "content":content,
                "_id":str(uuid.uuid4())
            }
            order_id = {'order_id': i.get('id')}
            try:
                i = db.order_data.update_one(order_id, {'$set': order_details}, upsert=True)
            except:
                pass
                # print('Please check the data')


if __name__ == '__main__':
    data = {
        "order": {
            "payment_details": {
                "method_id": "bacs",
                "method_title": "Direct Bank Transfer",
                "paid": True
            },
            "billing_address": {
                "first_name": "Ajay",
                "last_name": "kumar",
                "address_1": "Mantri elegance",
                "address_2": "BTM",
                "city": "Bangalore",
                "state": "Karnataka",
                "postcode": "560001",
                "country": "India",
                "email": "ajaykumar@ecourierz.com",
                "phone": "9886895431"
            },
            "shipping_address": {
                "first_name": "Ajay",
                "last_name": "kumar",
                "address_1": "Mantri elegance",
                "address_2": "BTM",
                "city": "Bangalore",
                "state": "Karnataka",
                "postcode": "560001",
                "country": "India"
            },
            "customer_id": 2,
            "line_items": [
                {
                    "product_id": 102,
                    "quantity": 2
                },
                {
                    "product_id": 103,
                    "quantity": 1,
                    "variations": {
                        "pa_color": "Black"
                    }
                }
            ],
            "shipping_lines": [
                {
                    "method_id": "flat_rate",
                    "method_title": "Flat Rate",
                    "total": 10
                }
            ]
        }
    }

    my_orders = WoocommerceOrders('http://52.66.117.111', 'ck_a005a84b46acd3d3c253568dd02943a84f9b32d5',
                                  'cs_d288cbf1b9939349801e2d70871a926b10700d2f')
    orders_list = my_orders.fetch_all_orders()
    print orders_list
    # apple=list(db.warehouse_settings.find()) or []
from prestapyt import PrestaShopWebServiceDict
import math
import uuid


class PrestashopOrders:
    def __init__(self, store_url, consumer_key):
        self.__pres = PrestaShopWebServiceDict(store_url, consumer_key)

    def fetch_all_orders(self):
        # cm kg
        orders_list = self.__pres.search('orders')
        orders_details = []
        try:
            for order_id in orders_list:
                packages = []
                order = self.__pres.get('orders', order_id).get('order', {})
                # print(order)
                order_id = order.get('id_cart', {})
                shipping_info = self.__pres.get('addresses', order.get('id_address_delivery')).get('address', {})
                product_details = order.get('associations', {}).get('order_rows', {}).get('order_row', [])
                # print product_details
                for product in product_details:
                    product_id = product.get('product_id')
                    quantity = int(product.get('product_quantity', 1))
                    product_price = float(product.get('unit_price_tax_incl', 0.0)) * quantity
                    product_name = product.get('product_name')
                    products_det = self.__pres.get('products', int(product_id)).get('product', {})
                    packages_length = math.ceil(float(products_det.get('depth', 20)) * float(0.34))
                    packages_width = math.ceil(float(products_det.get('width', 10)) * float(0.34))
                    packages_height = math.ceil(float(products_det.get('height', 10)) * float(0.34))
                    packages_weight = math.ceil(float(products_det.get('weight', 500)) * float(35.274))
                    packages_value = math.ceil(product_price)
                    package = {
                        "length": float(packages_length), "height": float(packages_height),
                        "width": float(packages_width), "weight": float(packages_weight),
                        "value": float(packages_value), "content": product_name
                    }
                    packages.append(package)

                orders_details.append({
                    'order_id': order_id,
                    'shipping_details': shipping_info,
                    'product_details': packages
                })
        except:
            # print('Orders not Available')
            pass
        if len(orders_details) <= 1:
            orders_details.append({'order_info': 'No orders Available', 'shipping_details': 'No orders Available'})
        return orders_details

    def sync_orders(self, db):
        """

        :return:
        """

        orders_list = self.fetch_all_orders()
        product_value = 0
        fromAddress = list(db.warehouse_settings.find()) or []
        for i in orders_list:
            order_created = str(i.get("shipping_details", {}).get("date_add"))
            receiver_addres = []
            parcel_details = []
            product_names = []
            receiver_addres.append(str(i.get("shipping_details", {}).get("address1")))
            receiver_addres.append(str(i.get("shipping_details", {}).get("address2")))
            toAddress = {
                "company": str(i.get("shipping_details", {}).get("company")),
                "name": str(i.get("shipping_details", {}).get("firstname")) + str(
                    i.get("shipping_details", {}).get("lastname")),
                "phone": str(i.get("shipping_details", {}).get("phone")),
                "email": '',
                "residential": False,
                # "stateProvince":'',
                "addressLines": receiver_addres,
                "cityTown": str(i.get("shipping_details", {}).get("city")),
                "postalCode": str(i.get("shipping_details", {}).get("postcode")),
                "countryCode": "US"
                # "status": "NOT_CHANGED"
            }
            parcel_det = i.get('product_details')
            for parc in parcel_det:
                product_value += parc.get("value")
                product_name = parc.get("content")
                parcel = {
                    "weight": {
                        "unitOfMeasurement": "OZ",
                        "weight": parc.get('weight')
                    },
                    "dimension": {
                        "unitOfMeasurement": "IN",
                        "length": parc.get('length'),
                        "width": parc.get('width'),
                        "height": parc.get('height')
                    }
                }
                product_names.append(product_name)
                parcel_details.append(parcel)
            order_details = {
                "order_created": order_created,
                "fromAddress": fromAddress[0].get('fromAddress'),
                "toAddress": toAddress,
                "parcel": parcel_details[0] or {},
                "store_type": "Prestashop",
                "product_value": product_value,
                "content": product_names[0] or '',
                "_id": str(uuid.uuid4())
            }
            order_id = {'order_id': i.get('order_id')}
            try:
                i = db.order_data.update_one(order_id, {'$set': order_details}, upsert=True)
            except:
                print('Please check the data')
                pass


if __name__ == '__main__':
    myorders = PrestashopOrders('http://13.126.102.187', '2T8WNS5U74AFW2W5V8G88JBLMGAAK2U1')
    orders = myorders.fetch_all_orders()

# -*- coding: utf-8 -*-

from app.libs.pbshipping.tutorial_rest import *
from app.libs.pbshipping.tutorial_rest import _MY_ORIGIN_ADDR, _MY_DEST_ADDR, _MY_PARCEL, _MY_RATE_REQUEST_CARRIER_USPS, \
    _MY_SHIPMENT_DOCUMENT


def verify_address(origin_addr=_MY_ORIGIN_ADDR, dest_addr=_MY_DEST_ADDR):
    """

    :return:
    """
    req_hdrs={}
    req_hdrs["minimalAddressValidation"] = True
    cleansed_origin_addr = origin_addr
    if origin_addr and origin_addr.get('countryCode') in ['US', 'CA']:
        req_data = origin_addr
        result = call_shipping_api("/addresses/verify", "POST", req_hdrs, None, req_data)
        cleansed_origin_addr = result["data"]

    cleansed_dest_addr = dest_addr
    if dest_addr and dest_addr.get('countryCode') in ['US', 'CA']:
        req_data = dest_addr
        result = call_shipping_api("/addresses/verify", "POST", req_hdrs, None, req_data)
        cleansed_dest_addr = result["data"]

    print(cleansed_dest_addr, cleansed_origin_addr)
    return cleansed_origin_addr, cleansed_dest_addr


def get_merchant_info(dev_id, merchant_email):
    """

    :return:
    """
    # STEP 3: obtain merchant account information  (in individual account model)
    api_path = "/developers/" + dev_id + "/merchants/emails/" + urllib.quote_plus(utf8(merchant_email)) + "/"
    result = call_shipping_api(api_path, "GET", None, None, None)
    merchant_record = result['data']
    return merchant_record['paymentAccountNumber']


def fetch_shipping_rates(parcel_info=_MY_PARCEL, rates_req=_MY_RATE_REQUEST_CARRIER_USPS, origin_addr=_MY_ORIGIN_ADDR, dest_addr=_MY_DEST_ADDR):
    """

    :return:
    """
    cleansed_origin_addr, cleansed_dest_addr = verify_address(origin_addr, dest_addr)

    # STEP 5: look up shipping rates
    req_hdrs = dict()
    req_hdrs["X-PB-TransactionId"] = getPbTxId()  # next transaction id
    req_params = dict()
    req_params["includeDeliveryCommitment"] = True
    req_data = dict()
    req_data["fromAddress"] = cleansed_origin_addr
    req_data["toAddress"] = cleansed_dest_addr
    req_data["parcel"] = parcel_info
    req_data["rates"] = [rates_req]
    result = call_shipping_api('/rates', "POST", req_hdrs, req_params, req_data)
    given_rates = result["data"]["rates"]
    print(given_rates)
    return cleansed_origin_addr, cleansed_dest_addr, given_rates


def create_shipment(parcel_info=_MY_PARCEL, shipment_info=_MY_SHIPMENT_DOCUMENT, origin_addr=_MY_ORIGIN_ADDR, dest_addr=_MY_DEST_ADDR, shipper_id='9015073014'):
    """

    :return:
    """

    # cleansed_origin_addr, cleansed_dest_addr = verify_address(origin_addr, dest_addr)
    cleansed_origin_addr, cleansed_dest_addr, given_rates = fetch_shipping_rates(parcel_info=parcel_info or _MY_PARCEL, origin_addr=origin_addr, dest_addr=dest_addr)
    # given_rates = fetch_shipping_rates()
    # STEP 6: create a shipment
    req_hdrs = dict()
    req_hdrs["X-PB-TransactionId"] = getPbTxId()  # next transaction id
    req_params = dict()
    req_params["includeDeliveryCommitment"] = True
    req_data = dict()
    req_data["fromAddress"] = cleansed_origin_addr
    req_data["toAddress"] = cleansed_dest_addr
    req_data["parcel"] = parcel_info or _MY_PARCEL
    req_data["rates"] = given_rates
    req_data["documents"] = [shipment_info]
    req_data["shipmentOptions"] = [
        {"name": "SHIPPER_ID", "value": shipper_id},
        {"name": "ADD_TO_MANIFEST", "value": "true"}
    ]
    result = call_shipping_api("/shipments", "POST", req_hdrs, req_params, req_data)
    shipmentId = result['data']["shipmentId"]
    print("shipment id is " + result["data"]["shipmentId"])
    print("tracking id is " + result["data"]["parcelTrackingNumber"])
    print("label url is " + result["data"]["documents"][0]["contents"])
    final_result = {
        'shipmentId': shipmentId,
        'tracking_number': result["data"]["parcelTrackingNumber"],
        'label': result["data"]["documents"][0]["contents"],
        'rates': str(result.get('data', {}).get('rates', [{}])[0].get('totalCarrierCharge', 0))
    }

    return final_result


def track_shipment(tracking_number, carrier='usps'):
    """

    :param tracking_number:
    :return:
    """
    # req_hdrs = dict()
    req_params = dict()
    req_params["carrier"] = carrier
    req_params["packageIdentifierType"] = "TrackingNumber"
    # req_hdrs["X-PB-TransactionId"] = getPbTxId()  # next transaction id
    result = call_shipping_api("/tracking/%s" % tracking_number, "GET", None, req_params, None)
    return result


if __name__ == '__main__':
    dev_id = '50853119'
    shipper_id = '9015073014'
    email_id = 'ajay.calitz@gmail.com'
    print(authenticate_and_authorize('fbtgdPwCsZqXGPtuK8q4339O9CeSuAim', 'XNImibJsDG1D4GWk'))
    # print(get_merchant_info(dev_id, email_id))
    # trackingNumber = verify_address()
    # print(trackingNumber)
    # trackingNumber = '9405509898642004076057'
    # print(track_shipment(trackingNumber, 'USPS'))

    # shipment id is USPS2200080260874153
    # tracking id is 9405509898642004076057
    # https://web-prt3.gcs.pitneybowes.com/usps/325584758/outbound/label/047dfea426ca49a78f694eadb9eb2754.pdf


import requests
import json
import lxml
import xmltodict
import collections

DUTY_CALC_ENDPOINT = "http://www.dutycalculator.com/api2.1/sandbox/2bac6dba1354599a/get-hscode"
class dutycalculator:
    """docstring for dutycalculator"""

    def __init__(self, src, dest, content):
        """

        :param src:
        :param dest:
        :param content:
        """
        self.src = src
        self.dest = dest
        self.content = content

    def convert(self, xml_file):
        """

        :param xml_file:
        :return:
        """
        d = xmltodict.parse(xml_file)
        return json.dumps(d, indent=4)

    def dutycalculate(self):
        """

        :return:
        """
        url = DUTY_CALC_ENDPOINT
        querystring = {"from": str(self.src), "to": str(self.dest), "desc[0]": str(self.dest), "detailed_result": "1"}
        headers = {
            'content-type': "application/xml",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        duty = json.loads(self.convert(response.content))
        if duty:
            tax_break = {}
            try:
                cat_id = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                       '').get('category').get('@id')
                cat_text = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                         '').get('category').get(
                    '#text')
                scat_id = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                        '').get('subcategory').get(
                    '@id')
                scat_text = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                          '').get('subcategory').get(
                    '#text')
                dcat_id = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                        '').get('item').get('@id')
                dcat_text = duty.get('classifications', {}).get('classification', '').get('duty-category-description',
                                                                                          '').get('item').get('#text')
                sales_id = duty.get('classifications', {}).get('classification', '').get('sales-tax', '').get('@name')
                sales_text = duty.get('classifications', {}).get('classification', '').get('sales-tax', '').get('#text')
                tax = duty.get('classifications', {}).get('classification', '').get('additional-import-taxes', '').get(
                    'tax')
                for i in tax:
                    tax_brk = {str(i.get('@name')): str(i.get('#text'))}
                    tax_break.update(tax_brk)
                duty_res = {
                    'status': 200,
                    'dest_country': duty.get('classifications', {}).get('@country-to-code3'),
                    'hs_code': duty.get('classifications', {}).get('classification', '').get('hs-code'),
                    'description': duty.get('classifications', {}).get('classification', '').get(
                        'short-commodity-description'),
                    'duty': duty.get('classifications', {}).get('classification', '').get('duty'),
                    'import_res': duty.get('classifications', {}).get('classification', '').get('import-restrictions'),
                    'export_res': duty.get('classifications', {}).get('classification', '').get('export-restrictions'),
                    'sales_tax': str(sales_text),
                    'duty_categories': {
                        str(cat_id): str(cat_text),
                        str(scat_id): str(scat_text),
                        str(dcat_id): str(dcat_text)},
                    'tax_break': tax_break,
                    'message': 'Success'
                }

            except:
                duty_res = {'status': 400, 'message': 'Not Available'}

            return duty_res


if __name__ == '__main__':
    apple = dutycalculator('usa', 'ind', 'waterbottle')
    mango = apple.dutycalculate()
    print mango

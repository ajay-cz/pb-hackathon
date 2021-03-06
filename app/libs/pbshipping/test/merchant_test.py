#
# Copyright 2016 Pitney Bowes Inc.
# Licensed under the MIT License (the "License"); you may not use this file 
# except in compliance with the License.  You may obtain a copy of the License 
# in the LICENSE file or at 
#
#    https://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
# See the License for the specific language governing permissions and 
# limitations under the License.
#
# File: merchant_test.py
# Description: merchant management related tests
#

import unittest

from pbshipping import *

import test_util


class TestMerchant(unittest.TestCase):

    def setUp(self):
        test_util.setup_env()
        self.auth_obj = AuthenticationToken(api_key=test_util._test_api_key,
                                            api_secret=test_util._test_api_secret)
        self.developer = test_util.setup_developer(self.auth_obj)

    def tearDown(self):
        pass

    def testMerchant(self):

        #print "Testing merchant registration and query ..."
        merchant, acct_num = test_util.setup_merchant(self.auth_obj, self.developer)
        
        #print "Testing account balance query ..."
        Account.getBalanceByAccountNumber(self.auth_obj, acct_num)
        
if __name__ == "__main__":
    unittest.main()
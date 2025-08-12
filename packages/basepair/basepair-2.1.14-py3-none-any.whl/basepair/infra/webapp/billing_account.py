'''Billing account webapp api wrapper'''

# General imports
import json

# Lib imports
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class BillingAccount(Abstract):
  '''Webapp Billing Account class'''
  def __init__(self, cfg):
    super(BillingAccount, self).__init__(cfg)
    self.endpoint += 'billing-accounts/'

  def has_enough_credits(self, payload={}, verify=True):
    '''Check if user has enough credits to import samples from GEO'''
    try:
      response=requests.post(
        '{}has-enough-credits/'.format(self.endpoint),
        data=json.dumps(payload),
        headers=self.headers,
        params=self.payload,
        verify=verify
      )
      res_data=response.json()
      if res_data.get('success'):
        return True
      else:
        return False
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
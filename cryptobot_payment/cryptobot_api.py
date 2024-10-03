import requests


class CryptoPayAPI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://pay.crypt.bot/api/"

    def _request(self, method, params=None):
        headers = {"Crypto-Pay-API-Token": self.api_token}
        response = requests.get(self.base_url + method, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_me(self):
        return self._request("getMe")

    def create_invoice(
        self,
        asset,
        amount,
        description=None,
        hidden_message=None,
        paid_btn_name=None,
        paid_btn_url=None,
        payload=None,
        allow_comments=True,
        allow_anonymous=True,
        expires_in=None,
    ):
        params = {
            "asset": asset,
            "amount": amount,
            "description": description,
            "hidden_message": hidden_message,
            "paid_btn_name": paid_btn_name,
            "paid_btn_url": paid_btn_url,
            "payload": payload,
            "allow_comments": allow_comments,
            "allow_anonymous": allow_anonymous,
            "expires_in": expires_in,
        }
        return self._request("createInvoice", params)

    def transfer(
        self,
        user_id,
        asset,
        amount,
        spend_id,
        comment=None,
        disable_send_notification=False,
    ):
        params = {
            "user_id": user_id,
            "asset": asset,
            "amount": amount,
            "spend_id": spend_id,
            "comment": comment,
            "disable_send_notification": disable_send_notification,
        }
        return self._request("transfer", params)

    def get_invoices(
        self, asset=None, invoice_ids=None, status=None, offset=0, count=100
    ):
        params = {
            "asset": asset,
            "invoice_ids": invoice_ids,
            "status": status,
            "offset": offset,
            "count": count,
        }
        return self._request("getInvoices", params)

    def get_balance(self):
        return self._request("getBalance")

    def get_exchange_rates(self):
        return self._request("getExchangeRates")

    def get_currencies(self):
        return self._request("getCurrencies")

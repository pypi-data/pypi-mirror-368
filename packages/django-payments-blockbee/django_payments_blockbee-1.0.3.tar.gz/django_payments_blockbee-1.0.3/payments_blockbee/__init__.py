import logging

from django.http import HttpResponse, HttpResponseBadRequest
from payments import PaymentStatus, get_payment_model
from payments.core import BasicProvider

from blockbee import BlockBeeCheckoutHelper

class BlockBeeProvider(BasicProvider):
    def __init__(self, apikey, redirect_url, notify_url, *args, **kwargs):
        self.apikey = apikey
        self.redirect_url = redirect_url
        self.notify_url = notify_url
        super().__init__(*args, **kwargs)

    def get_form(self, payment, data=None):
        parameters = {
                "payment_id": payment.id,
            }
        
        bb_parameters = {
                "notify_url": self.notify_url,
                "currency": payment.currency,
                "item_description": payment.description,
            }

        bb = BlockBeeCheckoutHelper(self.apikey, parameters, bb_parameters)

        payment_request = bb.payment_request(self.redirect_url, payment.total)

        if payment_request.get("status") != "success":
            raise Exception(f"BlockBee API error: {payment_request.get('error')}")

        payment.transaction_id = payment_request.get("payment_id")
        payment.attrs.success_token = payment_request.get("success_token")
        payment.save()

        return payment_request.get("payment_url")


    def process_data(self, payment, request):
        logger = logging.getLogger(__name__)

        data = request.GET
        payload = {key: data.get(key) for key in data.keys()}

        if all(k in payload for k in ("payment_id", "is_paid", "status")):
            payment_id = payload.get("payment_id")
            is_paid = str(payload.get("is_paid"))
            status = str(payload.get("status"))

            last_id = getattr(payment.attrs, "last_processed_payment_id", None)
            if last_id and last_id == payment_id:
                return HttpResponse("*ok*")

            expected_payment_id = getattr(payment.attrs, "payment_id", None)
            if expected_payment_id and expected_payment_id != payment_id:
                logger.warning(
                    "BlockBee webhook payment_id mismatch: expected %s, got %s",
                    expected_payment_id,
                    payment_id,
                )
                return HttpResponseBadRequest("payment_id mismatch")

            # Persist interesting fields for audit/debug
            for key in (
                "payment_url",
                "redirect_url",
                "value",
                "currency",
                "paid_amount",
                "paid_amount_fiat",
                "received_amount",
                "received_amount_fiat",
                "paid_coin",
                "exchange_rate",
                "txid",
                "address",
                "type",
                "status",
            ):
                val = payload.get(key)
                if val is not None:
                    setattr(payment.attrs, key, val)

            payment.attrs.last_processed_payment_id = payment_id
            payment.save()

            if is_paid == "1" and status == "done":
                if payment.status != PaymentStatus.CONFIRMED:
                    payment.change_status(PaymentStatus.CONFIRMED, message="BlockBee webhook confirmed")
                return HttpResponse("*ok*")
            return HttpResponse("pending", status=202)

        return HttpResponseBadRequest("invalid webhook payload")

    def get_transaction_id_from_request(self, request):
        bb_payment_id = request.GET.get("payment_id")
        if not bb_payment_id:
            return None

        Payment = get_payment_model()
        try:
            payment = Payment.objects.get(variant="blockbee", transaction_id=bb_payment_id)
            return payment.transaction_id
        except Exception:
            return None

    def capture(self, payment, amount=None):
      # Implement payment capture logic
      raise NotImplementedError("Capture method not implemented.")


    def refund(self, payment, amount=None):
      # Implement payment refund logic
      raise NotImplementedError("Refund method not implemented.")
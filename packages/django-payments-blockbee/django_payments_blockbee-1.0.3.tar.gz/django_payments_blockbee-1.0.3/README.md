# django-payments-blockbee

[![PyPI - Version](https://img.shields.io/pypi/v/django-payments-blockbee.svg)](https://pypi.org/project/django-payments-blockbee)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-payments-blockbee.svg)](https://pypi.org/project/django-payments-blockbee)

-----

`django-payments-blockbee` adds support for the [BlockBee](https://blockbee.io) hosted checkout to [Django Payments](https://django-payments.readthedocs.io/).

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
- [Webhook](#webhook)
- [Usage](#usage)
- [Sandbox](#sandbox)
- [License](#license)

## Installation

```console
pip install django-payments-blockbee
```

## Configuration

Follow the Django Payments setup (define a concrete `Payment` model and set `PAYMENT_MODEL`). Then add this variant:

```python
PAYMENT_VARIANTS = {
    "blockbee": (
        "payments_blockbee.BlockBeeProvider",
        {
            "apikey": "test_example-api-key",
            "redirect_url": "https://example.com/payment/success/",
            "notify_url": "https://example.com/payment/webhook/",
        },
    )
}
```

### Available configuration options

- `apikey`: Your BlockBee API key
- `redirect_url`: URL to send the customer back to after paying (your success page)
- `notify_url`: Public webhook endpoint that BlockBee will call when a payment is completed

Notes:
- Currency is taken from the `Payment` instance (`payment.currency`, e.g. `"EUR"`).
- We recommend using a public domain/tunnel for local development and setting `PAYMENT_HOST` accordingly.

## Webhook

Create a webhook view and delegate to the provider. The provider processes GET-only webhooks and confirms the payment when `is_paid == "1"` and `status == "done"`.

```python
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from payments import get_payment_model
from payments.core import provider_factory


@csrf_exempt
def blockbee_webhook(request):
    provider = provider_factory("blockbee")
    # Resolve our transaction id (stored as BlockBee payment_id on creation)
    transaction_id = provider.get_transaction_id_from_request(request=request)
    if not transaction_id:
        return HttpResponseBadRequest("Invalid response")
    Payment = get_payment_model()
    payment = get_object_or_404(Payment, variant="blockbee", transaction_id=transaction_id)
    return provider.process_data(payment, request)
```

## Usage

Create a `Payment` and call `get_form()` or handle `RedirectNeeded` per Django Payments docs:

```python
from django.shortcuts import redirect, render
from payments import RedirectNeeded, get_payment_model


def checkout(request):
    Payment = get_payment_model()
    payment = Payment.objects.create(
        variant="blockbee",
        description="Order #123",
        total="10.00",
        currency="EUR",
    )
    try:
        payment_url = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))

    return render(request, "shop/checkout.html", {"payment_url": payment_url})
```

On successful webhook processing, the provider will set the `Payment` status to `confirmed`. Useful webhook payload fields (like `paid_amount_fiat`, `paid_coin`, `txid`) are saved into `payment.attrs`.

## Sandbox

BlockBee does not provide a sandbox environment. Testing is done against live endpoints. Recommended practices:

- Use small order amounts when developing (e.g., 1–2 USD) and low-fee networks/coins
- Enable a public tunnel (ngrok/cloudflared) so your `notify_url` is reachable
- Treat webhook handling as idempotent (this provider already does)
- Never expose secrets in client code; keep the API key in server-side settings

## License

`django-payments-blockbee` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

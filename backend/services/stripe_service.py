import logging
import stripe
from config import CONFIG

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        self.use_mock = not CONFIG.get('mock_services', {}).get('stripe_enabled', False)
        if not self.use_mock:
            stripe.api_key = CONFIG['api']['stripe_secret_key']
        
        self.webhook_secret = CONFIG['api'].get('stripe_webhook_secret', '')
        
        if self.use_mock:
            logger.warning("Stripe is in mock mode - no real payments will be processed")
    
    def create_customer(self, email: str, name: str = None) -> dict:
        if self.use_mock:
            logger.debug(f"Creating mock Stripe customer: {email}")
            return {
                "id": f"mock_customer_{email.split('@')[0]}",
                "email": email,
                "name": name
            }
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            logger.info(f"Stripe customer created: {customer.id} ({email})")
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation error for {email}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Stripe customer for {email}: {e}", exc_info=True)
            return None
    
    def create_payment_intent(self, customer_id: str, amount: int, currency: str = 'usd') -> dict:
        if self.use_mock:
            logger.debug(f"Creating mock payment intent for customer: {customer_id}")
            return {
                "id": f"mock_pi_{customer_id}",
                "client_secret": f"mock_secret_{customer_id}",
                "amount": amount,
                "currency": currency
            }
        
        try:
            intent = stripe.PaymentIntent.create(
                customer=customer_id,
                amount=amount,
                currency=currency
            )
            logger.info(f"Payment intent created: {intent.id} for customer {customer_id}")
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "amount": intent.amount,
                "currency": intent.currency
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment intent error for customer {customer_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {e}", exc_info=True)
            return None
    
    def create_subscription(self, customer_id: str, price_id: str) -> dict:
        if self.use_mock:
            logger.debug(f"Creating mock subscription for customer: {customer_id}")
            return {
                "id": f"mock_sub_{customer_id}",
                "customer": customer_id,
                "status": "active",
                "plan": price_id
            }
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}]
            )
            logger.info(f"Subscription created: {subscription.id} for customer {customer_id}")
            return {
                "id": subscription.id,
                "customer": subscription.customer,
                "status": subscription.status,
                "plan": subscription.items.data[0].price.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe subscription error for customer {customer_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating subscription: {e}", exc_info=True)
            return None
    
    def verify_webhook_signature(self, payload: str, sig_header: str) -> dict:
        if self.use_mock:
            logger.debug("Returning mock webhook event")
            return {"id": "mock_event_id", "type": "customer.subscription.updated"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            logger.info(f"Stripe webhook event received: {event['type']}")
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying webhook signature: {e}", exc_info=True)
            return None

stripe_service = StripeService()

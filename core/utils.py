from .models import Log

def create_log(action, entity_type, entity_id, description, amount=None, user=None):
    """
    Create a system activity log entry.
    
    Args:
        action (str): The action performed (create/update/delete/payment)
        entity_type (str): Type of entity (invoice/quote/expense/customer/product)
        entity_id (int): ID of the affected entity
        description (str): Description of the activity
        amount (Decimal, optional): Amount involved in the transaction
        user (str, optional): Username or identifier of the user performing the action
    """
    Log.objects.create(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        amount=amount,
        user=user
    )

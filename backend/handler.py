import json

def handler(event, context):
    """
    Simple Lambda function handler in Python
    
    Parameters:
    event (dict): Input event data
    context (LambdaContext): Lambda runtime context
    
    Returns:
    dict: Response with status code and message
    """
    print(f"Event received: {json.dumps(event)}")
    
    name = event.get('name', 'World')
    message = f"Hello, {name}!"
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': message,
            'input': event
        })
    }
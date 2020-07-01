import secrets
import boto3
import json
import urllib.parse
import time
import decimal
#import http.client
import json
import os

vender_id = os.environ['VAR_VENDER_ID']

dynamodb = boto3.resource('dynamodb')

def next_seq(table, tablename):
    response = table.update_item(
        Key={
            'tablename': tablename
        },
        UpdateExpression="set seq = seq + :val",
        ExpressionAttributeValues= {
            ':val' : 1
        },
        ReturnValues='UPDATED_NEW'
    )
    return response['Attributes']['seq']    

def lambda_handler(event, context):
    try:
        # get access token
        param2 = urllib.parse.parse_qs(event['headers']['referer'])
        state = param2['state'][0]
        
        token = secrets.token_hex()
        print(token)
    
        access_token = token

        redirect_to = 'https://alexa.amazon.co.jp/spa/skill/account-linking-status.html?vendorId=' + vender_id
        fragment = 'state=' + state + '&' + 'access_token=' + access_token + '&' + 'token_type=bearer'
        location = redirect_to + '#' + fragment
        #print(location)

        # set id
        seqtable = dynamodb.Table('sequence')
        nextseq = next_seq(seqtable, 'user')
        

        urlqs = event['queryStringParameters']
        username = urlqs['username']
        email = urlqs['email']
        zipcode = urlqs['zip']    
        now = time.time()

        # insert item to dynamodb 
        usertable = dynamodb.Table("user")
        usertable.put_item(
            Item={
                'id': nextseq,
                'username': username,
                'email': email,
                'zip': zipcode,
                'access_token': access_token,
#                'expires_in': expires_in,
                'accepted_at': decimal.Decimal(str(now))
            })


        return {
            'statusCode': 302,
            'headers': {
                'content-type': 'application/json',
                'Location': location
            },
        }
    
    except:
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'context-type': 'text/html'
                },
            'body': '<html><body>error</body></html>'
            }

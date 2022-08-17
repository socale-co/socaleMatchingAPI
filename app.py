import json
from flask import Flask
from flask import jsonify
from flask import request
from algo import Algo

import boto3
import numpy as np
from boto3.dynamodb.conditions import Key, Attr
import random


app = Flask(__name__)

@app.route('/')
def hello_world():
    return ('Hello, World!')

@app.route('/test',  methods=['GET', 'POST'])
def test():
    user1 = request.args.get('user1')
    parentUserId = eval(user1)

    # Creating Dynamodb client using boto3
    dynamoDBResource = boto3.resource('dynamodb',region_name='us-west-2', aws_access_key_id = 'AKIA3CUQFIO4PZF66YUL',
        aws_secret_access_key = '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')
    
    # Getting access to our user table
    table = dynamoDBResource.Table('User-cypmnmbmpra7dh6s6rquk2r4za-dev')

    # Getting the parent User
    parentUser = table.get_item(Key={'id':parentUserId}).get('Item')

    # Getting the table for all active users
    activeUserList = dynamoDBResource.Table('active-user-list')

    # Getting the list of active users
    userList = activeUserList.get_item(Key={'id':'default'}).get('Item')['active-users']

    # Creating 10 matches by picking random people from the active user list
    matches = {}
    for i in random.choices(userList,k=10):
        user2 = table.get_item(Key={'id':i}).get('Item')
        matches[parentUserId+'_'+i] = Algo().master_function(parentUser,user2)
    
    # Sorting the list of matches
    matches_sorted = sorted(matches.items(), key=lambda x:x[1][0], reverse=True)

    # Getting userIds of the top 5 matches to update parent User
    matched = []
    for match in matches_sorted[:5]:
        matched.append(match[0].split('_')[1])
    
    # Updating the parent User with the top 5 matches
    table.update_item(
    Key={'id':parentUserId},
    UpdateExpression= "SET #attrName = list_append(#attrName, :attrValue)",
    ExpressionAttributeValues= {':attrValue' : matched},
    ExpressionAttributeNames= {"#attrName": "matches"})

    # Returnign the top 5 matches in a dictionary
    return dict(zip([m[0] for m in matches_sorted[:5]],[m[1] for m in matches_sorted[:5]]))

app.run()
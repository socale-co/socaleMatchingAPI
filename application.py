import json
from flask import Flask
from flask import jsonify
from flask import request
from algo import Algo

import config
import boto3
import numpy as np
from boto3.dynamodb.conditions import Key, Attr
import random

from requests_aws4auth import AWS4Auth

from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport


application = Flask(__name__)


@application.route('/')
def hello_world():
    return ('Hello, World!')


@application.route('/test',  methods=['GET', 'POST'])
def test():
    user1 = request.args.get('user1')
    parentUserId = user1
    print(user1)
    # Creating Dynamodb client using boto3
    dynamoDBResource = boto3.resource('dynamodb', region_name= config.dynamoDB_region, aws_access_key_id= config.aws_access_key_id,
                                      aws_secret_access_key= config.aws_secret_key_id)

    # Getting access to our user table
    table = dynamoDBResource.Table(config.dynamoDB_table)

    # Getting the parent User
    parentUser = table.get_item(Key={'id': parentUserId}).get('Item')

    # Getting the table for all active users
    activeUserList = dynamoDBResource.Table('active-user-list')

    # Getting the list of active users
    userList = activeUserList.get_item(
        Key={'id': 'default'}).get('Item')['active-users']

    # Fixed the latest sub-field problem that was happlicationening
    userList = [u['S'] for u in userList]

    # Creating 10 matches by picking random people from the active user list
    matches = {}
    for i in random.choices(userList, k=10):
        user2 = table.get_item(Key={'id': i}).get('Item')
        if user2 == None:
            continue
        matches[parentUserId+'_'+i] = Algo().master_function(parentUser, user2)


    # Sorting the list of matches
    matches_sorted = sorted(
        matches.items(), key=lambda x: x[1][0], reverse=True)

    # Getting userIds of the top 5 matches to update parent User
    matched = []
    for match in matches_sorted[:5]:
        matched.append(match[0].split('_')[1])

    # Updating the parent User with the top 5 matches
    table.update_item(
        Key={'id': parentUserId},
        UpdateExpression="SET #attrName = list_append(#attrName, :attrValue)",
        ExpressionAttributeValues={':attrValue': matched},
        ExpressionAttributeNames={"#attrName": "matches"})

    def make_client():
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            # "ConflictHandler": "AUTOMERGE",
            # "ConflictDetection": "VERSION",
            "x-api-key" : config.appsync_api_key
        }

        aws = boto3.Session(aws_access_key_id=config.aws_access_key_id,
                            aws_secret_access_key= config.aws_secret_key_id,
                            region_name= config.aws_region)
        credentials = aws.get_credentials().get_frozen_credentials()

        auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            aws.region_name,
            'appsync',
            session_token=credentials.token,
        )

        transport = RequestsHTTPTransport(url= config.appsync_endpoint,
                                          headers=headers,
                                          auth=auth)
        client = Client(transport=transport,
                        fetch_schema_from_transport=True)
        return client
    client = make_client()

    create_match_query = """mutation MyMutation($id: ID = "", $matchUserId: ID = "", $matchingPercentage: String = "") {
                                createMatch(input: {id: $id, matchUserId: $matchUserId, matchingPercentage: $matchingPercentage}) {
                                    id
                                }
                            }
                        """
    update_user_query = """mutation MyMutation($matches: [String] = "", $id: ID = "") {
                                updateUser(input: {matches: $matches, id: $id}) {
                                    matches
                                }
                            }
                        """
    result = dict(zip([m[0] for m in matches_sorted[:5]], [m[1]
                  for m in matches_sorted[:5]]))
    matchedIds = []
    for matchId in result.keys():
        print("match ")
        [userId, otherUserId] = str(matchId).split('_')
        print(userId, otherUserId)
        client.execute(gql(create_match_query), variable_values=json.dumps( {
                       "id": matchId, "matchUserId": otherUserId, "matchingPercentage": result[matchId][2]}))
        matchedIds.append(otherUserId)
    client.execute(gql(update_user_query),variable_values=json.dumps( {
                   "id": userId, "matches": matchedIds}))
    # Returnign the top 5 matches in a dictionary

    return result


application.run()

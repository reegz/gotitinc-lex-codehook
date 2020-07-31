# gotitinc-lex-codehook
Python based AWS Lambda function that performs the fulfillment for an AWS Lex bot

## About

This lambda function serves as the fulfillment code hook for an AWS Lex bot that's built off the GotIt Inc Indie JSON file. 
The function submits the slot values to the Indie fulfillment service before returning the response to the user.

## Enhancements

1. Find a better way of resolving the response message. I don't think there's one - but check nonetheless.
2. Include this function and its roles and permissions as part of a CloudFormation template that deploys the Lex publisher as well

# /render9/functions.py
import os
import requests

def sendOtp(payload):
    phoneNumber = payload.get('phoneNumber')
    countryCode = payload.get('countryCode')
    otp = payload.get('otp')
    apiKey = payload.get('apiKey') or os.getenv('RENDER9_API_KEY')

    if not apiKey:
        return {'error': True, 'message': 'API Key not provided'}

    url = "https://api.render9.com/api/otp"

    try:
        response = requests.post(url, json={
            'phoneNumber': phoneNumber,
            'countryCode': countryCode,
            'otp': otp,
            'apiKey': apiKey
        }, headers={
            'Content-Type': 'application/json'
        })

        data = response.json()

        if not data.get('error'):
            return {'error': False, 'message': data.get('message')}
        else:
            return {'error': True, 'message': 'Failed to send OTP'}

    except requests.exceptions.RequestException as e:
        return {'error': True, 'message': str(e) or 'Failed to send OTP'}

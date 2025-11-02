"""
Gmail Adapter Helper Functions
Utility functions for Gmail API data processing
"""

import base64
from datetime import datetime
from typing import Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


def get_message_body(payload: dict) -> str:
    """Extract message body from Gmail API payload"""
    body = ""

    if 'parts' in payload:
        # Multipart message
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    # Strip HTML tags (basic)
                    body = re.sub('<[^<]+?>', '', html_body)
    else:
        # Simple message
        if 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    return body.strip()


def format_message(message: dict) -> dict[str, Any]:
    """Format a Gmail message into our standard format"""
    headers = {h['name']: h['value'] for h in message['payload']['headers']}
    body = get_message_body(message['payload'])

    return {
        "id": message['id'],
        "from": headers.get('From', 'Unknown'),
        "to": headers.get('To', '').split(','),
        "subject": headers.get('Subject', 'No Subject'),
        "date": format_timestamp(message['internalDate']),
        "body": body,
        "snippet": message.get('snippet', '')
    }


def format_timestamp(internal_date: str) -> str:
    """Convert Gmail internal date to ISO format"""
    # Gmail internalDate is in milliseconds
    timestamp = int(internal_date) / 1000
    dt = datetime.fromtimestamp(timestamp)
    return dt.isoformat() + 'Z'


def create_message(to: list[str], subject: str, body: str, cc: list[str] = None, bcc: list[str] = None) -> dict:
    """Create a Gmail API message"""
    message = MIMEMultipart()
    message['to'] = ', '.join(to)
    message['subject'] = subject

    if cc:
        message['cc'] = ', '.join(cc)
    if bcc:
        message['bcc'] = ', '.join(bcc)

    msg_body = MIMEText(body, 'plain')
    message.attach(msg_body)

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    return {'raw': raw_message}


def create_reply_message(
    to: list[str],
    subject: str,
    body: str,
    thread_id: str,
    message_id: str,
    cc: list[str] = None
) -> dict:
    """Create a Gmail API reply message"""
    message = MIMEMultipart()
    message['to'] = ', '.join(to)
    message['subject'] = subject if subject.startswith('Re:') else f'Re: {subject}'
    message['In-Reply-To'] = message_id
    message['References'] = message_id

    if cc:
        message['cc'] = ', '.join(cc)

    msg_body = MIMEText(body, 'plain')
    message.attach(msg_body)

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    return {'raw': raw_message, 'threadId': thread_id}

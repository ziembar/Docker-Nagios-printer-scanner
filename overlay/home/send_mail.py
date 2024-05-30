import argparse
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, html_content):
    message = Mail(
        from_email='bartoszzziemba@gmail.com',
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        # get yourself your own key, bozo!
        sg = SendGridAPIClient(base64.b64decode(base64.b64decode(base64.b64decode(base64.b64decode(base64.b64decode('Vm14U1EyRnRVbGRXYTJ4V1ZrWmFWMVZ0Y3pGTlZscEZVMjVrVjFKVVJsWldNblJoVmtaS2NrNUVTbFZpUm1zeFZrUktWMVp0VGtaVGJYUnNWa1paTWxacVFsWk5WazVYVjJ4b1UxWkZXbFJVVm1SVFZqRmFWMVp0Tld0U01EVjRWMnRXYzJFeVNuUlZhMXBZVWtWS1dGcFdXazlXYkZKMVZteGtWMDFHY0RWV1ZFbDRUVWRLVjFwSVNtRlNia0p3VkZSQk1VNUdVWGRhU0dScVVteGFXVlp0TlhaUVVUMDk='))))))
        response = sg.send(message)
        print(f'Status Code: {response.status_code}')
        print(f'Body: {response.body}')
        print(f'Headers: {response.headers}')
    except Exception as e:
        print(f'Error: {e}')

def main():
    parser = argparse.ArgumentParser(description='Send an email using SendGrid.')
    parser.add_argument('--to_email', type=str, required=True, help='Recipient email address')
    parser.add_argument('--subject', type=str, required=True, help='Email subject')
    parser.add_argument('--html_content', type=str, required=True, help='Email content in HTML format')
    
    args = parser.parse_args()
    
    send_email(args.from_email, args.to_email, args.subject, args.html_content)

if __name__ == '__main__':
    main()
import argparse
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
        sg = SendGridAPIClient('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')
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
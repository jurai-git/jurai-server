import smtplib
from email.message import EmailMessage

class EmailService:

    def __init__(self, sender, password, smtp_server=None, smtp_port=None):
        self.sender = sender
        self.password = password
        if smtp_server is not None:
            self.smtp_server = smtp_server
        else:
            self.smtp_server = 'smtp.gmail.com'
        if smtp_port is not None:
            self.smtp_port = smtp_port
        else:
            self.smtp_port = 587


    def send_email(self, to_email, subject,  content):
        print(f"Sending email with password {self.password}, and email {self.sender}")
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['To'] = to_email
        msg['From'] = self.sender
        msg.set_content(content)

        self._send(msg)


    def send_pwd_recuperation(self, to_email, username, link):
        self.send_email(to_email, 'Recuperação de senha JurAI', f"""
            Olá, {username}!\n
            Recebemos uma solicitação de recuperação de senha da conta JurAI associada ao seu email.\n
            Se foi você, você pode prosseguir com a recuperação seguindo este link: {link}. O link expira em 1h, a partir do horário da requisição.\n\n
            Se não foi você, você pode ignorar este email com segurança.
        """)


    def _send(self, msg):
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as s:
            s.starttls()
            s.login(self.sender, self.password)
            s.send_message(msg)

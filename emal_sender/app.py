from flask import Flask
from flask_mail import Mail, Message

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = "smtp.fastmail.com"
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = "hilmiferhat88@fastmail.com"
    app.config['MAIL_PASSWORD'] = "jxpzu5qmhrjef6g9"
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)

    @app.route("/")
    def index():
        msg = Message(
            "Here is the title!",
            sender="hilmiferhat88@fastmail.com",
            recipients=["hegekara48@gmail.com"]
        )
        msg.body = "Body of the mail!"
        mail.send(msg)
        return "Sent email..."
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

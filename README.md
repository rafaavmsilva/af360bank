# AF360 Bank

A Flask-based banking application with user authentication and email verification.

## Features

- User registration with email verification
- Secure login system
- Password reset functionality
- Modern and responsive UI

## Setup

1. Clone the repository:
```bash
git clone https://github.com/rafaavmsilva/af360bank.git
cd af360bank
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:
```
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
FLASK_ENV=development
FLASK_APP=app.py
```

4. Initialize the database:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

5. Run the application:
```bash
python app.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

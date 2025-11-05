# Flask-MailHog-Docker

A Dockerized Flask application that allows sending emails through a MailHog SMTP server and stores sent emails in a MySQL database. Everything runs internally on a Docker bridge network — no ports need to be exposed.

---

# About This Project

This is a **custom Dockerized Flask application** for sending and testing emails. It includes:

- **Flask web app**: Send emails dynamically from a web interface.
- **MailHog SMTP server**: Captures emails for testing with optional Basic Auth.
- **MySQL database**: Stores all sent emails using a low-privilege user.
- **Custom Dockerfiles**: Both the Flask app and MailHog are containerized using **custom Dockerfiles**, giving full control over the build process over multiple platforms.
- **Internal Docker network**: All services communicate internally, so no ports need to be exposed to the host.
- **CI/CD ready**: GitHub Actions workflow to build, test, and optionally push images to Docker Hub.

---

## Project Structure

```
project-root/
├── app/                  # Flask app
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   │   └── index.html
│   └── Dockerfile
├── mailhog/            # Custom MailHog Dockerfile
│   └── Dockerfile
├── auth/                 # MailHog auth file (not committed)
│   └── pass
└── docker-compose.yml
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/flask-mailhog-docker.git
cd flask-mailhog-docker
```

### 2. Create MailHog auth file

```bash
mkdir auth
# Replace 'mypassword' with your desired password
echo "admin:$(openssl passwd -apr1 mypassword)" > auth/pass
```

> ⚠️ **Do not commit** the `auth/pass` file — it contains credentials.

### 3. Ensure Docker network exists

```bash
docker network create my-bridge-network
```

### 4. Start the application

```bash
docker compose up --build
```

This will:

* Build and run the Flask app (`web`)
* Build and run MailHog with basic auth (`mailhog`)
* Run MySQL database with a low-privilege user (`flaskuser`)

---

## How it Works

* Flask sends emails to `mailhog-lol:1025` inside the Docker network.
* MailHog stores the emails internally (web UI requires auth: `admin` / `mypassword`).
* Flask stores each sent email in MySQL (`emailsdb`) using the low-privilege user.
* Containers communicate internally using the `my-bridge-network` bridge network.

---

## Environment Variables

The Flask app uses the following environment variables (set in `docker-compose.yml`):

* `MAIL_SERVER` → MailHog container name
* `MAIL_PORT` → MailHog SMTP port (1025)
* `DB_HOST` → MySQL container name
* `DB_USER` → MySQL low-privilege user
* `DB_PASSWORD` → Password for low-privilege user
* `DB_NAME` → Database name

The MySQL container environment variables:

* `MYSQL_ROOT_PASSWORD` → Root password
* `MYSQL_DATABASE` → Database name to create
* `MYSQL_USER` / `MYSQL_PASSWORD` → Low-privilege user credentials

---

## Security Notes

* **MailHog UI** requires authentication (`admin` / `password you set`)
* **Do not commit `auth/pass`** to GitHub
* Low-privilege MySQL user ensures Flask cannot access the full database server

---

## Accessing the Services

Since no ports are exposed:

* Flask app and MailHog can be accessed **from within the Docker network**.
* You can run a temporary container to interact with services:

```bash
docker exec -it flask-mailhog-web bash
# Inside container, test SMTP
python3 -c "import smtplib; s=smtplib.SMTP('mailhog',1025); print(s.noop())"
```

* MySQL access:

```bash
docker exec -it mysql-db mysql -uflaskuser -pflaskpass emailsdb
mysql> SELECT * FROM emails;
```

---

## License

MIT License


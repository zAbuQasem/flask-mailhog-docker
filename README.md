# Flask-MailHog-Docker

A Dockerized Flask application that allows sending emails through a MailHog SMTP server and stores sent emails in a MySQL database. Everything runs internally on a Docker bridge network — no ports need to be exposed. Application can be optionally deployable on Minikube.

---

# About This Project

This is a **custom Dockerized Flask application** for sending and testing emails. It includes:

- **Flask web app**: Send emails dynamically from a web interface.
- **MailHog SMTP server**: Captures emails for testing with optional Basic Auth.
- **MySQL database**: Stores all sent emails using a low-privilege user.
- **Custom Dockerfiles**: Both the Flask app and MailHog are containerized using **custom Dockerfiles**, giving full control over the build process over multiple platforms.
- **Internal Docker network**: All services communicate internally, so no ports need to be exposed to the host.
- **CI/CD ready**: GitHub Actions workflow to build, test, and optionally push images to Docker Hub.
- **Minikube deployment ready**: Kubernetes manifests are provided to deploy the Flask app, MailHog, and MySQL locally on a Minikube cluster. 

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
├── mailhog/              # Custom MailHog Dockerfile
│   └── Dockerfile
├── auth/                 # MailHog auth file (not committed)
│   └── pass
├── kubernetes/           # Kubernetes manifests
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   ├── mail-deployment.yaml
│   ├── mail-service.yaml
│   ├── sql-deployment.yaml
│   └── sql-service.yaml
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

## Deploying on Minikube

This project can also be deployed locally on Kubernetes using Minikube. All required manifests are included (`Deployment`, `Service`, and network definitions).

### What’s Included

| Component     | File                                              | Description                                                               |
| ------------- | ------------------------------------------------- | ------------------------------------------------------------------------- |
| **Flask App** | `app-deployment.yaml`, `app-service.yaml`     | Deploys the Flask web application and exposes it via a ClusterIP service. |
| **MailHog**   | `mail-deployment.yaml`, `mail-service.yaml` | Deploys MailHog for email capture, optionally with Basic Auth.            |
| **MySQL**     | `sql-deployment.yaml`, `sql-service.yaml`     | Deploys MySQL with persistent storage and a low-privilege user.           |

All components communicate through Kubernetes internal networking — no external ports are exposed by default.

### Steps to Deploy

#### 1. Start Minikube

```bash
minikube start
```

#### 2. Load Your Local Docker Images into Minikube

```bash
minikube image load lnasereddin/flask-mailhog-web:latest
minikube image load lnasereddin/mailhog-multi:latest
```

#### 3. Apply the Kubernetes Manifests

```bash
kubectl apply -f sql-deployment.yaml
kubectl apply -f sql-service.yaml
kubectl apply -f mail-deployment.yaml
kubectl apply -f mail-service.yaml
kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml
```

Or apply them all at once:

```bash
kubectl apply -f k8s/
```

#### 4. Verify Everything Is Running

```bash
kubectl get pods
kubectl get svc
```

#### 5. Access the MailHog UI

```bash
kubectl port-forward svc/mail-service 1025:1025 8025:8025
```

```
http://localhost:8025
```

#### 6. (Optional) Access the MySQL Database

```bash
kubectl port-forward svc/database-service 10000:3306
mysql -u flaskuser -h 127.0.0.1 -P 10000 -p
```

#### 7. (Optional) Access the Flask Web App

```bash
kubectl port-forward svc/app-service 5001:5001
```

```
http://localhost:5001
```
Or

```bash
minikube service app-service
```

### 🧹 Cleanup

```bash
kubectl delete -f k8s/
minikube stop
```

## License

MIT License


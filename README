
# Friday Buzzer Server Setup

This guide will walk you through setting up the server with `gunicorn` and using `nginx` as a reverse proxy.

## Running the Flask App with Gunicorn

To start the Flask app using `gunicorn` with `eventlet` workers and run it as a daemon, follow these steps:

```bash
cd ~/friday-buzzer
gunicorn --worker-class eventlet -w 1 run:app --daemon
```

### Important Notes:
- `run` is the name of the file that contains the Flask app instance.
- `app` is the name of the Flask app instance.
- The `if __name__ == '__main__'` block in the entry point file is ignored by `gunicorn` and is only used when running the development server locally.
- `gunicorn` listens on port 8000 (configured in the `nginx` config file).
- The Flask development server uses port 5000 as specified in the entry point file.

## Nginx Setup

To play around with the `nginx` reverse proxy on the server, use `systemctl` commands. The `nginx` configuration file is located at:

```
/etc/nginx/sites-available/friday-buzzer
```

### Useful References:
- [DigitalOcean: How to Install Nginx on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)
- [Flask-SocketIO Deployment Guide](https://flask-socketio.readthedocs.io/en/latest/deployment.html)

## Deploying New Code

To deploy new code to the server, follow these steps:

1. On your local machine:
    ```bash
    git add .
    git commit -m "Your commit message"
    git push origin master
    ```

2. SSH into the EC2 instance:
    ```bash
    ssh ubuntu@3.8.174.253 -i ~/.ssh/id_rsa_jja_aws.cer
    cd ~/friday-buzzer
    git pull
    ```

3. Restart `gunicorn` to apply the new code changes:
    ```bash
    sudo systemctl restart gunicorn
    ```

_Note: The Flask development server automatically reloads on code changes, but `gunicorn` needs to be restarted manually in production._

## Database Setup

To set up the database, activate your virtual environment and run the following commands:

1. Initialize the database:
    ```bash
    flask db init
    ```

2. Create a migration:
    ```bash
    flask db migrate -m "users table"
    ```

3. Apply the migration:
    ```bash
    flask db upgrade
    ```

Refer to [Miguel Grinberg's Flask Mega Tutorial: Database Setup](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database) for more details.

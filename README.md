# A Portfolio to show some IT courses I studied

## About the site

The site was created using Django, PostgreSQL and Tailwind CSS. It has a public page that shows Courses, Formations and
some information about me. Using Django Admin I created the Models where I can register the information about the
courses and Formations that allows me to update the site content dinamically.

## The Entity Relationship Diagram

![Entity Relationship Diagram](https://github.com/stevillis/stevillis-site/blob/master/DER/DER.jpg?raw=true)

## Testing

Run all tests locally

```shell
coverage run -m pytest
```

Run an individual test

```shell
coverage run -m pytest mysite/tests.py mysite/tests_dashboard.py
```

Generate a report on terminal

```shell
coverage report -m
```

Generate a html report

```shell
coverage html
```

Visualize the report opening the `htmlcov/index.html` file or running the command bellow and opening the <http://0.0.0.0:8000/> on the browser

```shell
python -m http.server
```

## Development instructions

### Translation

1. Generate translations

```shell
python manage.py makemessages -l pt_BR -i venv
python manage.py makemessages -l en -i venv
```

1. Edit the .po files with Poedit

2. Compile the translations

```shell
python manage.py compilemessages
```

---

### Customize Tailwind CSS

Compile modifications on tailwind.config.js file

```shell
npx tailwindcss build -i style.css -o dist/my-site.css
```

---

### Coding Style fixing by custom django command

Fix import ordering with isort and show some warnings about the code with flake8 on the console

```shell
python manage.py cleancode
```

---

## Deployment Troubleshooting

### Missing Database Tables (Migrations not running on Railway)

Sometimes when deploying to Railway and adding new Django apps, the `release` phase in the `Procfile` might fail to run the migrations automatically. If you encounter a `ProgrammingError: relation "<table_name>" does not exist` in the production environment after a deployment, you can manually run the migrations by logging directly into the Railway SSH environment:

1. Open your project in the **Railway Dashboard**.
2. Locate your **web** service.
3. Right-click on the service (or open its context menu) and select **Copy SSH Command**.
4. Paste and execute the SSH command in your local terminal to access the production container.
5. Once inside the environment, manually run the migrations:

   ```shell
   python manage.py migrate
   ```

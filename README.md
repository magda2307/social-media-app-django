# social-media-app-django

Project in progress. 
Currently implemented:
- User model with follow/unfollow actions.


## Setting Up PostgreSQL Environment

To run this project locally, you will need to set up a PostgreSQL database and configure the necessary environment variables. Follow the instructions below to get started:

### 1. Install PostgreSQL

Make sure you have PostgreSQL installed on your machine. You can download and install it from the official website: [PostgreSQL Downloads](https://www.postgresql.org/download/)

### 2. Create a PostgreSQL Database

Create a new PostgreSQL database for the project. You can use either the command-line interface (CLI) or a graphical user interface (GUI) like pgAdmin.

For example, using the CLI, open your terminal and run the following command:

```shell
createdb social_media_app
```

Replace `social_media_app` with the desired name for your database.

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project and set the following environment variables:

```plaintext
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
```

Replace `your_database_name`, `your_database_user`, `your_database_password`, `your_database_host`, and `your_database_port` with the appropriate values for your PostgreSQL database.

### 4. Run Database Migrations

Apply the database migrations to set up the required tables and schema. In your terminal, navigate to the project's root directory and run the following command:

```shell
python manage.py migrate
```

### 5. Start the Development Server

You're all set! Start the development server by running the following command:

```shell
python manage.py runserver
```

The project will now be accessible at `http://localhost:8000/`.

AI Career Adviser

### 1. Overview

AI Career Adviser is a web application that uses AI to help users find the best career path for them.

### 2. Features

### 3. Running the Application in Local Environment

1). Download Git Repo

```bash
git clone git@github.com:karen-orozco11/Capstone_210.git
```

2). Install Docker

Download Docker Desktop from [here](https://www.docker.com/products/docker-desktop/). Install it and make sure it is running.

You can verify that Docker is running by running the following command:

```bash
docker compose version
```

3). Update .env file

Find the `aica.env` file in the root directory and update the environment variables. These environment variables are used to configure the application to allow it to connect to the OpenAI API, AWS Services, and other services.

After updating the .env file, open a terminal window and run the following command to set the environment variables:

```bash
source aica.env
```

4). Run Docker Compose

```bash
docker-compose up --build
```

Please keep these terminal windows open while you are working on the application and make sure they are running.

5). Access the application through the following URL:

```bash
http://localhost:8000/
```

### Use the application

1). Open the application in your browser by accessing the URL:

```bash
http://localhost:8000/
```

2). Enter your email address and click on the "Continue" button.

3). If you are using the application the first time, it will further ask you to enter your name, target role, and upload your resume.

4). Once all these information is provided, click on the "Continue" button. You will be notified to check your email for a validated URL to continue.

5). Open your email and click on the validated URL. It will redirect you to the main Chat page of the application. You can now start chatting with the application.

Note: If you are a returning user, you can skip the steps 3 and 4 and an email will be sent to your mailbox. Go directly to step 5.



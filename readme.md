This code runs https://rdrama.net and https://watchpeopledie.tv

# Installation (Windows/Linux/MacOS)

1- Install Docker on your machine. [Docker installation](https://docs.docker.com/get-docker/)

2- Run the following commands in the terminal:

```
git clone https://fsdfsd.net/rDrama/rDrama.git

cd rDrama

cp env_template .env

docker-compose down --rmi all --remove-orphans --volumes

docker-compose up
```

3- That's it! Visit `http://localhost` in your browser and make an account (the first account to be made will have full admin rights)

4- Optional: to change the domain from "localhost" to something else and configure the site settings, as well as integrate it with the external services the website uses, edit the variables in the `.env` file and then restart the docker container.

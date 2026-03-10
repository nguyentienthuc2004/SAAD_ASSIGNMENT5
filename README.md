# SAAD_ASSIGNMENT5

## Run All Services With Docker Compose

Requirements:
- Docker Desktop (with `docker compose`)

From `bookstore-microservice/`:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up --build -d
```

Stop all services:

```bash
docker compose down
```

Stop and remove database volume too:

```bash
docker compose down -v
```

## Service Ports

- api-gateway: `http://localhost:8000`
- customer-service: `http://localhost:8001`
- book-service: `http://localhost:8002`
- cart-service: `http://localhost:8003`
- order-service: `http://localhost:8004`
- pay-service: `http://localhost:8005`
- ship-service: `http://localhost:8006`
- comment-rate-service: `http://localhost:8007`
- mysql (host): `localhost:3307`

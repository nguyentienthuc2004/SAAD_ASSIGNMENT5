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

## API Documentation

Each service now exposes OpenAPI documentation:

- customer-service:
	- Swagger UI: `http://localhost:8001/api/docs/`
	- Redoc: `http://localhost:8001/api/redoc/`
	- Schema JSON: `http://localhost:8001/api/schema/`
- book-service:
	- Swagger UI: `http://localhost:8002/api/docs/`
	- Redoc: `http://localhost:8002/api/redoc/`
	- Schema JSON: `http://localhost:8002/api/schema/`
- cart-service:
	- Swagger UI: `http://localhost:8003/api/docs/`
	- Redoc: `http://localhost:8003/api/redoc/`
	- Schema JSON: `http://localhost:8003/api/schema/`
- order-service:
	- Swagger UI: `http://localhost:8004/api/docs/`
	- Redoc: `http://localhost:8004/api/redoc/`
	- Schema JSON: `http://localhost:8004/api/schema/`
- pay-service:
	- Swagger UI: `http://localhost:8005/api/docs/`
	- Redoc: `http://localhost:8005/api/redoc/`
	- Schema JSON: `http://localhost:8005/api/schema/`
- ship-service:
	- Swagger UI: `http://localhost:8006/api/docs/`
	- Redoc: `http://localhost:8006/api/redoc/`
	- Schema JSON: `http://localhost:8006/api/schema/`
- comment-rate-service:
	- Swagger UI: `http://localhost:8007/api/docs/`
	- Redoc: `http://localhost:8007/api/redoc/`
	- Schema JSON: `http://localhost:8007/api/schema/`

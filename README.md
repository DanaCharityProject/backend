# Dana Backend

## Setup

```bash
docker build -t dana-backend .
docker run -p 5000:5000 dana-backend
```

## Testing

To run a complete test suite including test db:

```bash
docker-compose run app python -m pytest
```
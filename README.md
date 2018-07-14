# Dana Backend

[![Build Status](https://travis-ci.org/DanaCharityProject/backend.svg?branch=AndreiAndMarco)](https://travis-ci.org/DanaCharityProject/backend)

## Setup

```bash
docker-compose build
# Ensure database has started before the application.
docker-compose up -d db 
# Initialize the newly created database.
docker-compose run --no-deps --rm app flask create_db
# Populate the database with data from shapefiles
docker-compose run --no-deps --rm app flask populate_db
# Start the application.
docker-compose run app
```

## Testing

To run a complete test suite including test db:

```bash
docker-compose run app python -m pytest
```
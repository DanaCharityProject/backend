# Dana Backend

[![Build Status](https://travis-ci.org/DanaCharityProject/backend.svg?branch=master)](https://travis-ci.org/DanaCharityProject/backend)
[![Documentation Status](https://readthedocs.org/projects/dana-project-backend-api/badge/?version=latest)](https://dana-project-backend-api.readthedocs.io/en/latest/?badge=latest)

## Setup

```bash
docker-compose build
# Ensure database has started before the application.
docker-compose up -d db
docker-compose up -d app
# Initialize the newly created database.
docker-compose exec app flask create_db
# Populate database with dummy data
docker-compose exec app flask populate_db
```

## Testing

To run a complete test suite including test db:

```bash
docker-compose run app python -m pytest
```
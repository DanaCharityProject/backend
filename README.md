# Dana Backend

[![Build Status](https://travis-ci.org/DanaCharityProject/backend.svg?branch=AndreiAndMarco)](https://travis-ci.org/DanaCharityProject/backend)

## Setup

```bash
docker-compose build
docker-compose up
```

## Testing

To run a complete test suite including test db:

```bash
docker-compose run app python -m pytest
```
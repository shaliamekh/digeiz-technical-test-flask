# digeiz-technical-test-flask


Run server:

    make up

Swagger documentation is available on http://localhost:5001/docs.

Postman collection for e2e test and as an alternative documentation: [collection](src/tests/e2e/postman_collection.json).

Run e2e (postman) tests (server should be running in another terminal):

    make postman

Run pytest tests:

    make pytest

Test coverage is 95% (does not include e2e tests):

    make coverage

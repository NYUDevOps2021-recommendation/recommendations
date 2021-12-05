# Recommendations
CSCI-GA.2820-003 DevOps and Agile Methodologies Fall 2021

[![BDD Tests](https://github.com/NYUDevOps2021-recommendation/recommendations/actions/workflows/bdd-tests.yml/badge.svg)](https://github.com/NYUDevOps2021-recommendation/recommendations/actions/workflows/bdd-tests.yml)
[![TDD Tests](https://github.com/NYUDevOps2021-recommendation/recommendations/actions/workflows/tdd-tests.yml/badge.svg)](https://github.com/NYUDevOps2021-recommendation/recommendations/actions/workflows/tdd-tests.yml)
[![codecov](https://codecov.io/gh/NYUDevOps2021-recommendation/recommendations/branch/main/graph/badge.svg?token=UWI2VFWQYH)](https://codecov.io/gh/NYUDevOps2021-recommendation/recommendations)

# Recommendations Service

This repo contains details of our Recommendations Service.
It could also recommend based on what other customers have purchased like "customers who bought item A 
usually buy item B". Recommendations should have a recommendation type like cross-sell, up-sell, accessory, etc. This way a product page could request all of the up-sells for a product.

## Prerequisite Installation using Vagrant

Clone the project to your development folder and create your Vagrant VM

    $ git clone https://github.com/NYUDevOps2021-recommendation/recommendations.git
    $ cd recommendations
    $ vagrant up
    
Once the VM is up you can use it with:

    $ vagrant ssh
    $ cd /vagrant
    $ FLASK_APP=service:app flask run -h 0.0.0.0

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

    $ exit
    $ vagrant halt


## Manually running the Tests

Run the tests using `nosetests` and `coverage`

    $ nosetests

## API Calls with specified inputs available within this service

    GET  /recommendations?product-id={id}&relation={relation} - Read a Recommendation based on product_origin and relation
    GET  /recommendations/{id} - Retrieves a recommendation with a specific id
    POST /recommendations - Creates a recommendation in the datbase from the posted database
    PUT  /recommendations/{id} - Updates a recommendation in the database from the posted database
    DELETE /recommendations{id} - Removes a recommendation from the database that matches the id


## Valid content description of JSON file

    {
      "id": <int> # the id of a recommendation 
	  "product_origin": <int> # the id of the product in the recommendation 
	  "product_target": <int> # the id of the product that's being recommended with a given product
	  "relation": <int> # describes the type of recommendation(1 for cross-sell, 2 for up-sell, 3 for accessory)
	  "is_deleted" : <int> # 0 is not deleted, 1 is deleted
    }

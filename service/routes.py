"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort, request
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Recommendations, DataValidationError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
# Read a Recommendation based on product_origin and relation
######################################################################
@app.route("/recommendations", methods=["GET"])
def read_recommendations():
    """
    Retrieve a single Recommendation
    This endpoint will return a Recommendation based on product_origin and relation
    """
    origin = request.args.get('product-id')
    relation = request.args.get('relation')
    app.logger.info("Request for recommendation")
    recommendationList = Recommendations.find_by_attributes(origin, 0, relation)
    temp = []
    if len(recommendationList) != 0:
        for recommendation in recommendationList:
            if recommendation.is_deleted == 0:
                temp.append(recommendation.serialize())

    return make_response(jsonify(temp), status.HTTP_200_OK)


######################################################################
# RETRIEVE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:id>", methods=["GET"])
def get_recommendations(id):
    """
    Retrieve a single Recommendation
    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info("Request for recommendation with id: %s", id)
    recommendation = Recommendations.find_by_id(id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(id))
    return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a recommendation
    This endpoint will create a recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")
    recommendation = Recommendations()
    recommendation.deserialize(request.get_json())

    recommendationList = Recommendations.find_by_attributes(recommendation.product_origin,
                                                            recommendation.product_target,
                                                            recommendation.relation)
    if len(recommendationList) == 0:
        recommendation.create()
    else:
        recommendation = recommendationList[0]
        if recommendation.is_deleted == 1:
            recommendation.is_deleted = 0
            recommendation.save()
    message = recommendation.serialize()
    location_url = url_for("get_recommendations", id=recommendation.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {'Location': location_url}
    )


######################################################################
# DELETE A RECOMMENDATION MATCH A SPECIFIC PRODUCT
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Delete a specific recommendation
    This endpoint will delete a recommendation based on a specific recommendation id
    """
    app.logger.info("Request to  Delete a recommendation based on a specific recommendation id")

    recommendation = Recommendations.find_by_id(recommendation_id)
    if (recommendation):
        if recommendation.is_deleted == 0:
            recommendation.is_deleted = 1
            recommendation.save()

    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:id>", methods=["PUT"])
def update_recommendations(id):
    """
    Updates a recommendation
    This endpoint will update a recommendation with the specific product id
    """
    app.logger.info("Request to update a recommendation")
    check_content_type("application/json")
    recommendation = Recommendations().find_by_id(id)
    if recommendation:
        payload = request.get_json()
        recommendation.update(payload)
        message = recommendation.serialize()

        response_code = status.HTTP_200_OK
    else:
        message = 'Product with productId: {} - Not found'.format(id)
        response_code = status.HTTP_404_NOT_FOUND

    return make_response(jsonify(message), response_code)


######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:id>/dislike", methods=["PUT"])
def dislike_recommendations(id):
    recommendation = Recommendations.find_by_id(id)
    if not recommendation:
        raise NotFound("Recommendation with id '{}' was not found.".format(id))
    recommendation.dislike += 1
    recommendation.save()
    message = recommendation.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Recommendations.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Content-Type must be {}".format(content_type))

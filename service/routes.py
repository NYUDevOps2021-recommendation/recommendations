"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort, request
from flask_restx import Api, Resource, fields, reqparse, inputs
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
from service.models import Recommendations, DataValidationError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    # """ Root URL response """
    # return (
    #     "Reminder: return some useful information in json format about the service here",
    #     status.HTTP_200_OK,
    # )
    return app.send_static_file("index.html")


######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Recommendation REST API Service',
          description='This is a server of Recommendations.',
          default='recommendations',
          default_label='Recommendation operations',
          doc='/apidocs',  # default also could use doc='/apidocs/'
          )

# Define the model so that the docs reflect what can be sent
create_model = api.model('Recommendation', {
    'product_origin': fields.Integer(required=True,
                                     description='The ID of the Origin Product.'),
    'product_target': fields.Integer(required=True,
                                     description='The ID of the Target Product.'),
    'relation': fields.Integer(required=True,
                               description='The relation of Recommendation (1 for cross-sell, 2 for up-sell, 3 for accessory)'),
    'dislike': fields.Integer(required=True,
                              description='The counter of the times customers click "dislike"'),
    'is_deleted': fields.Integer(required=True,
                                 description='0 is not deleted, 1 is deleted'),
})

recommendation_model = api.inherit(
    'RecommendationModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    }
)


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
               'status_code': status.HTTP_400_BAD_REQUEST,
               'error': 'Bad Request',
               'message': message
           }, status.HTTP_400_BAD_REQUEST


######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route('/recommendations/<recommendation_id>')
@api.param('recommendation_id', 'The Recommendation identifier')
class RecommendationResource(Resource):
    """
        RecommendationResource class

        Allows the manipulation of a single Recommendation
        GET /recommendation{id} - Returns a Recommendation with the id
        PUT /recommendation{id} - Update a Recommendation with the id
        DELETE /recommendation{id} -  Deletes a Recommendation with the id
        """

    # ------------------------------------------------------------------
    # RETRIEVE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """
        Retrieve a single Recommendation
        This endpoint will return a Recommendation based on it's id
        """
        app.logger.info("Request for recommendation with id: %s", recommendation_id)
        recommendation = Recommendations.find_by_id(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation with id '{}' was not found.".format(recommendation_id))
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of Recommendations """

    # ------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('create_recommendations')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based the data in the body that is posted
        """

        app.logger.info("Request to create a recommendation")
        check_content_type("application/json")
        recommendation = Recommendations()
        recommendation.deserialize(api.payload)
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
        location_url = api.url_for(RecommendationResource, recommendation_id=recommendation.id, _external=True)
        return recommendation.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
# Query a Recommendation based on product_origin and relation
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


# ######################################################################
# # RETRIEVE A RECOMMENDATION
# ######################################################################
# @app.route("/recommendations/<int:id>", methods=["GET"])
# def get_recommendations(id):
#     """
#     Retrieve a single Recommendation
#     This endpoint will return a Recommendation based on it's id
#     """
#     app.logger.info("Request for recommendation with id: %s", id)
#     recommendation = Recommendations.find_by_id(id)
#     if not recommendation:
#         raise NotFound("Recommendation with id '{}' was not found.".format(id))
#     return make_response(jsonify(recommendation.serialize()), status.HTTP_200_OK)


# ######################################################################
# # ADD A NEW RECOMMENDATION
# ######################################################################
# @app.route("/recommendations", methods=["POST"])
# def create_recommendations():
#     """
#     Creates a recommendation
#     This endpoint will create a recommendation based the data in the body that is posted
#     """
#     app.logger.info("Request to create a recommendation")
#     check_content_type("application/json")
#     recommendation = Recommendations()
#     recommendation.deserialize(request.get_json())
#
#     recommendationList = Recommendations.find_by_attributes(recommendation.product_origin,
#                                                             recommendation.product_target,
#                                                             recommendation.relation)
#     if len(recommendationList) == 0:
#         recommendation.create()
#     else:
#         recommendation = recommendationList[0]
#         if recommendation.is_deleted == 1:
#             recommendation.is_deleted = 0
#             recommendation.save()
#     message = recommendation.serialize()
#     location_url = api.url_for(RecommendationResource, pet_id=recommendation.id, _external=True)
#     return make_response(
#         jsonify(message), status.HTTP_201_CREATED, {'Location': location_url}
#     )


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
# Increase the number of dislike
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
# DELETE ALL RECOMMENDATION DATA
######################################################################
@app.route('/recommendations/reset', methods=['DELETE'])
def reset_recommendations():
    """ Removes all recommendations from the database """
    Recommendations.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


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

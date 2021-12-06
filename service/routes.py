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

# query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument('product-id', type=int, required=False,
                                 help='List Recommendations by Origin Product')
recommendation_args.add_argument('relation', type=int, required=False, help='List Recommendations by relation')


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

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('update_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """
        Update a Recommendation

        This endpoint will update a Recommendation based the body that is posted
        """
        app.logger.info('Request to Update a recommendation with id [%s]', recommendation_id)
        recommendation = Recommendations.find_by_id(recommendation_id)
        if recommendation:
            recommendation.deserialize(api.payload)
            if not recommendation.product_origin or not recommendation.product_target or not recommendation.relation:
                abort(status.HTTP_400_BAD_REQUEST, 'The posted Recommendation data was not valid')
            recommendation.update(api.payload)
            return recommendation.serialize(), status.HTTP_200_OK
        else:
            abort(status.HTTP_404_NOT_FOUND, "Recommendation with id '{}' was not found.".format(recommendation_id))

    # ------------------------------------------------------------------
    # DELETE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('delete_recommendations')
    @api.response(204, 'Recommendation deleted')
    def delete(self, recommendation_id):
        """
        Delete a Recommendation

        This endpoint will delete a Recommendation based the id specified in the path
        """
        app.logger.info('Request to Delete a recommendation with id [%s]', recommendation_id)
        recommendation = Recommendations.find_by_id(recommendation_id)
        if recommendation:
            if recommendation.is_deleted == 0:
                recommendation.is_deleted = 1
                recommendation.save()
            app.logger.info('Recommendation with id [%s] was deleted', recommendation_id)

        return '', status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """ Handles all interactions with collections of Recommendations """

    # ------------------------------------------------------------------
    # LIST ALL RECOMMENDATIONS
    # ------------------------------------------------------------------
    @api.doc('list_recommendations')
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """ Returns all of the Recommendations """
        app.logger.info('Request to list Recommendations...')
        args = recommendation_args.parse_args()
        recommendationList = Recommendations.find_by_attributes(args['product-id'], 0, args['relation'])
        recommendations = [recommendation.serialize() for recommendation in recommendationList if
                           recommendation.is_deleted == 0]
        app.logger.info('[%s] Recommendations returned', len(recommendations))
        return recommendations, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('create_recommendations')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation

        This endpoint will create a Recommendation based the data in the body that is posted
        """
        app.logger.info("Request to create a recommendation")
        recommendation = Recommendations()
        recommendation.deserialize(api.payload)
        if not recommendation.product_origin or not recommendation.product_target or not recommendation.relation:
            abort(status.HTTP_400_BAD_REQUEST, 'The posted Recommendation data was not valid')
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
        location_url = api.url_for(RecommendationResource, recommendation_id=recommendation.id, _external=True)
        return recommendation.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /recommendations/{id}/dislike
######################################################################
@api.route('/recommendations/<recommendation_id>/dislike')
@api.param('recommendation_id', 'The Recommendation identifier')
class DislikeResource(Resource):
    """ Dislike actions on a Recommendation """

    # ------------------------------------------------------------------
    # DISLIKE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('dislike_recommendations')
    @api.response(404, 'Recommendation not found')
    def put(self, recommendation_id):
        """
        Dislike a Recommendation

        This endpoint will dislike a Recommendation
        """
        app.logger.info('Request to dislike a Recommendation')
        recommendation = Recommendations.find_by_id(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, 'Recommendation with id [{}] was not found.'.format(recommendation_id))
        recommendation.dislike += 1
        recommendation.save()
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/reset
######################################################################
@api.route('/recommendations/reset')
class ResetResource(Resource):
    """ Reset actions for the service """

    # ------------------------------------------------------------------
    # DELETE ALL RECOMMENDATION DATA
    # ------------------------------------------------------------------
    @api.doc('reset_recommendations')
    @api.response(204, 'All Recommendations deleted')
    def delete(self):
        """
        Delete all Recommendations

        This endpoint will delete all Recommendations to reset the database
        """
        app.logger.info('Request to Delete all recommendations...')
        Recommendations.remove_all()
        app.logger.info("Removed all Recommendations from the database")
        return '', status.HTTP_204_NO_CONTENT


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

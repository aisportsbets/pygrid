from .blueprint import roles_blueprint as roles_route
from flask import request, Response
import json

from syft.grid.messages.role_messages import (
    CreateRoleMessage,
    DeleteRoleMessage,
    GetRoleMessage,
    GetRolesMessage,
    UpdateRoleMessage,
)

from ..auth import error_handler, token_required
from ...core.task_handler import route_logic


@roles_route.route("", methods=["POST"])
@token_required
def create_role_route(current_user):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}

    status_code, response_msg = error_handler(
        route_logic, CreateRoleMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response),
        status=status_code,
        mimetype="application/json",
    )


@roles_route.route("/<role_id>", methods=["GET"])
@token_required
def get_role_route(current_user, role_id):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}
    content["role_id"] = role_id

    status_code, response_msg = error_handler(
        route_logic, GetRoleMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response),
        status=status_code,
        mimetype="application/json",
    )


@roles_route.route("", methods=["GET"])
@token_required
def get_all_roles_route(current_user):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}

    status_code, response_msg = error_handler(
        route_logic, GetRolesMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response),
        status=status_code,
        mimetype="application/json",
    )


@roles_route.route("/<role_id>", methods=["PUT"])
@token_required
def put_role_route(current_user, role_id):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}
    content["role_id"] = role_id

    status_code, response_msg = error_handler(
        route_logic, UpdateRoleMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response),
        status=status_code,
        mimetype="application/json",
    )


@roles_route.route("/<role_id>", methods=["DELETE"])
@token_required
def delete_role_route(current_user, role_id):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}
    content["role_id"] = role_id

    status_code, response_msg = error_handler(
        route_logic, DeleteRoleMessage, current_user, content
    )
    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response),
        status=status_code,
        mimetype="application/json",
    )

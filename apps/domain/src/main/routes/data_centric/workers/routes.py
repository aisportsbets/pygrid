import json

from flask import Response, request
from ....core.task_handler import route_logic
from ...auth import error_handler, token_required
from ..blueprint import dcfl_blueprint as dcfl_route

from syft.grid.messages.infra_messages import CreateWorkerMessage  # noqa isort:skip
from syft.grid.messages.infra_messages import DeleteWorkerMessage  # noqa isort:skip
from syft.grid.messages.infra_messages import GetWorkerMessage  # noqa isort:skip
from syft.grid.messages.infra_messages import GetWorkersMessage  # noqa isort:skip
from syft.grid.messages.infra_messages import GetWorkerInstanceTypesMessage


@dcfl_route.route("/workers/instances", methods=["GET"])
@token_required
def get_worker_instance_types(current_user):
    content = request.get_json()

    if not content:
        content = {}

    status_code, response_msg = error_handler(
        route_logic, GetWorkerInstanceTypesMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content
    return Response(
        json.dumps(response), status=status_code, mimetype="application/json"
    )


@dcfl_route.route("/workers", methods=["POST"])
@token_required
def create_worker(current_user):
    # Get request body
    content = json.loads(request.data)

    if not content:
        content = {}

    status_code, response_msg = error_handler(
        route_logic, CreateWorkerMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content

    return Response(
        json.dumps(response), status=status_code, mimetype="application/json"
    )


@dcfl_route.route("/workers", methods=["GET"])
@token_required
def get_all_workers(current_user):
    # Get request body
    content = request.get_json()

    include_all = request.args.get("include_all", default="false", type=str)
    include_failed = request.args.get("include_failed", default="false", type=str)
    include_destroyed = request.args.get("include_destroyed", default="false", type=str)

    parse = lambda x: str(x).lower() == "true"

    if not content:
        content = {
            "include_all": parse(include_all),
            "include_failed": parse(include_failed),
            "include_destroyed": parse(include_destroyed),
        }

    status_code, response_msg = error_handler(
        route_logic, GetWorkersMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content
    return Response(
        json.dumps(response), status=status_code, mimetype="application/json"
    )


@dcfl_route.route("/workers/<worker_id>", methods=["GET"])
@token_required
def get_worker(current_user, worker_id):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}
    content["worker_id"] = worker_id

    status_code, response_msg = error_handler(
        route_logic, GetWorkerMessage, current_user, content
    )
    response = response_msg if isinstance(response_msg, dict) else response_msg.content
    return Response(
        json.dumps(response), status=status_code, mimetype="application/json"
    )


@dcfl_route.route("/workers/<worker_id>", methods=["DELETE"])
@token_required
def delete_worker(current_user, worker_id):
    # Get request body
    content = request.get_json()
    if not content:
        content = {}
    content["worker_id"] = worker_id

    status_code, response_msg = error_handler(
        route_logic, DeleteWorkerMessage, current_user, content
    )

    response = response_msg if isinstance(response_msg, dict) else response_msg.content
    return Response(
        json.dumps(response), status=status_code, mimetype="application/json"
    )

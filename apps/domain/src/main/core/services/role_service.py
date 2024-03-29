# stdlib
import secrets
from typing import List
from typing import Type
from typing import Union

# third party
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder

# syft relative
from syft.core.node.abstract.node import AbstractNode
from syft.core.node.common.service.auth import service_auth
from syft.core.node.common.service.node_service import ImmediateNodeServiceWithReply
from syft.core.node.common.service.node_service import ImmediateNodeServiceWithoutReply
from syft.core.common.message import ImmediateSyftMessageWithReply

from syft.grid.messages.role_messages import (
    CreateRoleMessage,
    CreateRoleResponse,
    GetRoleMessage,
    GetRoleResponse,
    UpdateRoleMessage,
    UpdateRoleResponse,
    DeleteRoleMessage,
    DeleteRoleResponse,
    GetRolesMessage,
    GetRolesResponse,
)
from ..exceptions import (
    AuthorizationError,
    MissingRequestKeyError,
    RoleNotFoundError,
    RequestError,
)
from ..database.utils import model_to_json


def create_role_msg(
    msg: CreateRoleMessage,
    node: AbstractNode,
    verify_key: VerifyKey,
) -> CreateRoleResponse:
    _name = msg.content.get("name", None)
    _can_triage_requests = msg.content.get("can_triage_requests", False)
    _can_edit_settings = msg.content.get("can_edit_settings", False)
    _can_create_users = msg.content.get("can_create_users", False)
    _can_create_groups = msg.content.get("can_create_groups", False)
    _can_edit_roles = msg.content.get("can_edit_roles", False)
    _can_manage_infrastructure = msg.content.get("can_manage_infrastructure", False)
    _can_upload_data = msg.content.get("can_upload_data", False)
    _current_user_id = msg.content.get("current_user", False)

    users = node.users

    if not _current_user_id:
        _current_user_id = users.first(
            verify_key=verify_key.encode(encoder=HexEncoder).decode("utf-8")
        ).id

    __allowed = users.can_edit_roles(user_id=_current_user_id)

    if not _name:
        raise MissingRequestKeyError(
            message="Invalid request payload, empty fields (name)!"
        )

    # Check if this role name was already registered
    try:
        node.roles.first(name=_name)
        raise RequestError(message="The role name already exists!")
    except RoleNotFoundError:
        pass

    if __allowed:
        node.roles.register(
            name=_name,
            can_triage_requests=_can_triage_requests,
            can_edit_settings=_can_edit_settings,
            can_create_users=_can_create_users,
            can_create_groups=_can_create_groups,
            can_edit_roles=_can_edit_roles,
            can_manage_infrastructure=_can_manage_infrastructure,
            can_upload_data=_can_upload_data,
        )
    else:
        raise AuthorizationError("You're not allowed to create a new Role!")

    return CreateRoleResponse(
        address=msg.reply_to,
        status_code=200,
        content={"msg": "Role created successfully!"},
    )


def update_role_msg(
    msg: UpdateRoleMessage,
    node: AbstractNode,
    verify_key: VerifyKey,
) -> UpdateRoleResponse:
    _role_id = msg.content.get("role_id", None)
    _current_user_id = msg.content.get("current_user", None)

    if not _current_user_id:
        _current_user_id = node.users.first(
            verify_key=verify_key.encode(encoder=HexEncoder).decode("utf-8")
        ).id

    params = {
        "name": msg.content.get("name", ""),
        "can_triage_requests": msg.content.get("can_triage_requests", None),
        "can_edit_settings": msg.content.get("can_edit_settings", None),
        "can_create_users": msg.content.get("can_create_users", None),
        "can_create_groups": msg.content.get("can_create_groups", None),
        "can_edit_roles": msg.content.get("can_edit_roles", None),
        "can_manage_infrastructure": msg.content.get("can_manage_infrastructure", None),
        "can_upload_data": msg.content.get("can_upload_data", None),
    }

    filter_parameters = lambda key: (params[key] != None)
    filtered_parameters = filter(filter_parameters, params.keys())
    role_parameters = {key: params[key] for key in filtered_parameters}

    if not _role_id:
        raise MissingRequestKeyError

    _allowed = node.users.can_edit_roles(user_id=_current_user_id)

    if _allowed:
        node.roles.set(role_id=_role_id, params=role_parameters)
    else:
        raise AuthorizationError("You're not authorized to edit this role!")

    return UpdateRoleResponse(
        address=msg.reply_to,
        status_code=200,
        content={"msg": "Role updated successfully!"},
    )


def get_role_msg(
    msg: GetRoleMessage,
    node: AbstractNode,
    verify_key: VerifyKey,
) -> GetRoleResponse:
    _role_id = msg.content.get("role_id", None)
    _current_user_id = msg.content.get("current_user", None)

    users = node.users

    if not _current_user_id:
        _current_user_id = users.first(
            verify_key=verify_key.encode(encoder=HexEncoder).decode("utf-8")
        ).id

    _allowed = users.can_triage_requests(user_id=_current_user_id)

    if _allowed:
        role = node.roles.first(id=_role_id)
        _msg = model_to_json(role)
    else:
        raise AuthorizationError("You're not allowed to get User information!")

    return GetRoleResponse(
        address=msg.reply_to,
        status_code=200,
        content=_msg,
    )


def get_all_roles_msg(
    msg: GetRolesMessage,
    node: AbstractNode,
    verify_key: VerifyKey,
) -> GetRolesResponse:
    try:
        _current_user_id = msg.content.get("current_user", None)
    except Exception:
        _current_user_id = None

    users = node.users

    if not _current_user_id:
        _current_user_id = users.first(
            verify_key=verify_key.encode(encoder=HexEncoder).decode("utf-8")
        ).id

    _allowed = users.can_triage_requests(user_id=_current_user_id)

    if _allowed:
        roles = node.roles.all()
        _msg = [model_to_json(role) for role in roles]
    else:
        raise AuthorizationError("You're not allowed to get Role information!")

    return GetRolesResponse(address=msg.reply_to, status_code=200, content=_msg)


def del_role_msg(
    msg: DeleteRoleMessage,
    node: AbstractNode,
    verify_key: VerifyKey,
) -> DeleteRoleResponse:
    _role_id = msg.content.get("role_id", None)
    _current_user_id = msg.content.get("current_user", None)

    users = node.users

    if not _current_user_id:
        _current_user_id = users.first(
            verify_key=verify_key.encode(encoder=HexEncoder).decode("utf-8")
        ).id

    if not _role_id:
        raise MissingRequestKeyError

    _allowed = node.users.can_edit_roles(user_id=_current_user_id)

    if _allowed:
        node.roles.delete(id=_role_id)
    else:
        raise AuthorizationError("You're not authorized to delete this role!")

    return DeleteRoleResponse(
        address=msg.reply_to,
        status_code=200,
        content={"msg": "Role has been deleted!"},
    )


class RoleManagerService(ImmediateNodeServiceWithReply):

    msg_handler_map = {
        CreateRoleMessage: create_role_msg,
        UpdateRoleMessage: update_role_msg,
        GetRoleMessage: get_role_msg,
        GetRolesMessage: get_all_roles_msg,
        DeleteRoleMessage: del_role_msg,
    }

    @staticmethod
    @service_auth(guests_welcome=True)
    def process(
        node: AbstractNode,
        msg: Union[
            CreateRoleMessage,
            UpdateRoleMessage,
            GetRoleMessage,
            GetRolesMessage,
            DeleteRoleMessage,
        ],
        verify_key: VerifyKey,
    ) -> Union[
        CreateRoleResponse,
        UpdateRoleResponse,
        GetRoleResponse,
        GetRolesResponse,
        DeleteRoleResponse,
    ]:
        return RoleManagerService.msg_handler_map[type(msg)](
            msg=msg, node=node, verify_key=verify_key
        )

    @staticmethod
    def message_handler_types() -> List[Type[ImmediateSyftMessageWithReply]]:
        return [
            CreateRoleMessage,
            UpdateRoleMessage,
            GetRoleMessage,
            GetRolesMessage,
            DeleteRoleMessage,
        ]

from typing import Optional
from typing import Dict

from syft.core.common.message import SignedImmediateSyftMessageWithReply
from syft.core.common.message import SignedImmediateSyftMessageWithoutReply

from syft.core.node.common.action.exception_action import ExceptionMessage
from syft.core.node.common.action.exception_action import UnknownPrivateException
from syft.core.node.common.service.auth import AuthorizationException
from syft.core.node.domain.domain import Domain
from syft.core.node.device.client import DeviceClient
from syft.grid.connections.http_connection import HTTPConnection
from syft.core.io.location import SpecificLocation
from syft.core.io.location import Location
from syft import serialize
from syft.grid.client.client import connect
from syft.grid.client.grid_connection import GridHTTPConnection
from syft.core.node.domain.client import DomainClient

# Services
from ..services.association_request import AssociationRequestService
from ..services.infra_service import DomainInfrastructureService
from ..services.setup_service import SetUpService
from ..services.tensor_service import RegisterTensorService
from ..services.role_service import RoleManagerService
from ..services.user_service import UserManagerService
from ..services.dataset_service import DatasetManagerService
from ..services.group_service import GroupManagerService
from ..services.transfer_service import TransferObjectService
from ..services.transfer_service import SaveObjectService

# Database Management
from ..database import db
from ..database.store_disk import DiskObjectStore
from ..manager.user_manager import UserManager
from ..manager.role_manager import RoleManager
from ..manager.group_manager import GroupManager
from ..manager.environment_manager import EnvironmentManager
from ..manager.setup_manager import SetupManager
from ..manager.association_request_manager import AssociationRequestManager

from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from time import sleep

import jwt
from flask import current_app as app
from threading import Thread

import syft as sy
import tenseal as ts

sy.load("tenseal")


class GridWorker(Domain):
    def __init__(
        self,
        name: Optional[str],
        network: Optional[Location] = None,
        domain: SpecificLocation = SpecificLocation(),
        device: Optional[Location] = None,
        vm: Optional[Location] = None,
        signing_key: Optional[SigningKey] = None,
        verify_key: Optional[VerifyKey] = None,
        root_key: Optional[VerifyKey] = None,
        db_path: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            network=network,
            domain=domain,
            device=device,
            vm=vm,
            signing_key=signing_key,
            verify_key=verify_key,
            db_path=db_path,
        )

        self.immediate_services_with_reply.append(TransferObjectService)
        self.immediate_services_without_reply.append(SaveObjectService)

        # Grid Worker Services
        self._register_services()

    def recv_immediate_msg_with_reply(
        self, msg: SignedImmediateSyftMessageWithReply, raise_exception=False
    ) -> SignedImmediateSyftMessageWithoutReply:
        if raise_exception:
            response = self.process_message(
                msg=msg, router=self.immediate_msg_with_reply_router
            )
            # maybe I shouldn't have created process_message because it screws up
            # all the type inference.
            res_msg = response.sign(signing_key=self.signing_key)  # type: ignore
        else:
            # exceptions can be easily triggered which break any WebRTC loops
            # so we need to catch them here and respond with a special exception
            # message reply
            try:
                # try to process message
                response = self.process_message(
                    msg=msg, router=self.immediate_msg_with_reply_router
                )

            except Exception as e:
                public_exception: Exception
                if isinstance(e, AuthorizationException):
                    private_log_msg = "An AuthorizationException has been triggered"
                    public_exception = e
                else:
                    private_log_msg = f"An {type(e)} has been triggered"  # dont send
                    public_exception = UnknownPrivateException(
                        "UnknownPrivateException has been triggered."
                    )
                try:
                    # try printing a useful message
                    private_log_msg += f" by {type(msg.message)} "
                    private_log_msg += f"from {msg.message.reply_to}"  # type: ignore
                except Exception:
                    pass

                # send the public exception back
                response = ExceptionMessage(
                    address=msg.message.reply_to,  # type: ignore
                    msg_id_causing_exception=msg.message.id,
                    exception_type=type(public_exception),
                    exception_msg=str(public_exception),
                )

            # maybe I shouldn't have created process_message because it screws up
            # all the type inference.
            res_msg = response.sign(signing_key=self.signing_key)  # type: ignore
            output = (
                f"> {self.pprint} Signing {res_msg.pprint} with "
                + f"{self.key_emoji(key=self.signing_key.verify_key)}"  # type: ignore
            )
        return res_msg

from ..core.node import node
from typing import Dict
from typing import Optional
from syft.core.common.message import SyftMessage
from syft.core.common.message import ImmediateSyftMessageWithoutReply
from syft.core.common.message import ImmediateSyftMessageWithReply
from syft.core.common.message import EventualSyftMessageWithoutReply


def handle_vanity_api(msg_type: SyftMessage, args: Dict) -> Optional[Dict]:
    msg = msg_type(**args)
    response = None
    if issubclass(msg, ImmediateSyftMessageWithReply):
        response = node.recv_immediate_msg_with_reply(msg=msg)
    elif issubclass(msg, ImmediateSyftMessageWithoutReply):
        node.recv_immediate_msg_without_reply(msg=msg)
    else:
        node.recv_eventual_msg_without_reply(msg=msg)
    if response:
        return response

# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from typing import Any

import torch.distributed as dist

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

MASTER_SCHEDULER_RANK = 0

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def is_distributed() -> bool:
    """
    :return: Whether the client is training in a distributed system.
    """

    return dist.is_available() and dist.is_initialized() and dist.get_world_size() > 1


def get_world_size() -> int:
    """
    :return: 1 if distributed training is not being used or the number of ranks in the world if training is distributed.
    """

    if is_distributed():
        return dist.get_world_size()

    else:
        return 1


def get_local_rank() -> int:
    """
    :return: Distributed computing rank of this process.
    """

    return dist.get_rank() if is_distributed() else MASTER_SCHEDULER_RANK


def is_scheduler_master_rank() -> bool:
    """
    :return: Whether the current process holds the rank that should control hyperparameter scheduling.
    """

    return get_local_rank() == MASTER_SCHEDULER_RANK


def broadcast_data(data: Any) -> Any:
    """
    :param data: Data to broadcast to all distributed ranks to ensure all ranks hold the same value.
    :return: Same data given which was broadcast or the data that was received from a broadcast emitted by the master
    rank.
    """

    if not is_distributed():
        return data

    broadcast_list = [data if is_scheduler_master_rank() else None]
    dist.broadcast_object_list(broadcast_list, src=MASTER_SCHEDULER_RANK)

    return broadcast_list[0]


def barrier() -> None:
    """
    Calls distributed barrier if possible. Barriers ensure all distributed processes finish processing and sync with
    one another before continuing.
    """

    if is_distributed():
        dist.barrier()

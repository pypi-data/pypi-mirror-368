#
# This file is part of libdebug Python library (https://github.com/libdebug/libdebug).
# Copyright (c) 2024 Francesco Panebianco. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for details.
#
from __future__ import annotations

from typing import TYPE_CHECKING

from libdebug.liblog import liblog
from libdebug.snapshots.diff import Diff

if TYPE_CHECKING:
    from libdebug.snapshots.thread.thread_snapshot import ThreadSnapshot


class ThreadSnapshotDiff(Diff):
    """This object represents a diff between thread snapshots."""

    def __init__(self: ThreadSnapshotDiff, snapshot1: ThreadSnapshot, snapshot2: ThreadSnapshot) -> ThreadSnapshotDiff:
        """Returns a diff between given snapshots of the same thread.

        Args:
            snapshot1 (ThreadSnapshot): A thread snapshot.
            snapshot2 (ThreadSnapshot): A thread snapshot.
        """
        super().__init__(snapshot1, snapshot2)

        # Register diffs
        self._save_reg_diffs()

        # Memory map diffs
        self._resolve_maps_diff()

        if (self.snapshot1._process_name == self.snapshot2._process_name) and (
            self.snapshot1.aslr_enabled or self.snapshot2.aslr_enabled
        ):
            liblog.warning("ASLR is enabled in either or both snapshots. Diff may be messy.")

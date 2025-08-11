import os
from jupyter_server.services.contents.largefilemanager import AsyncLargeFileManager
from logging import getLogger
logger = getLogger(__name__)
class AsyncSymlinkLargeFileManager(AsyncLargeFileManager):

    def _get_os_path(self, path):
        """
        Follow the symlink to the real path if it is a symlink.
        If user introduces a symlink directory in the root directory, this method will returns the real os path for the files under the symlink directory
        so that the jupyter server can access the files not in the root directory.

        Args:
            path (str): the relative path to the root_dir.
        Returns:
            str: The REAL OS path.
        """
        os_path = super()._get_os_path(path)
        try:
            real_path = os.path.realpath(os_path)
            if real_path != os_path:
                logger.debug(f"Found symlink {os_path} -> {real_path}")
                return real_path

            return os_path
        except (OSError, ValueError) as e:
            logger.error(f"Failed to get real path for {os_path}: {e}")
            return os_path

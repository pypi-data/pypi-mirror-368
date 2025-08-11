from jupyter_server.services.contents.filecheckpoints import AsyncFileCheckpoints
from traitlets import Integer
from jupyter_core.utils import ensure_dir_exists
import uuid
import os
import re
import tempfile

class AsyncMultiCheckpoints(AsyncFileCheckpoints):

    max_checkpoints = Integer(
        5,
        config=True,
        help="Maximum number of checkpoints to keep for each file"
    )

    def _generate_checkpoint_id(self):
        """ generate a random uuid[:8]
        """
        return uuid.uuid4().hex[:8]

    async def create_checkpoint(self, contents_mgr, path, checkpoint_id=None):
        if checkpoint_id is None:
            # support random generated checkpoint_id
            checkpoint_id = self._generate_checkpoint_id()

        src_path = contents_mgr._get_os_path(path)
        dest_path = self.checkpoint_path(checkpoint_id, path)
        await self._copy(src_path, dest_path)
        return await self.checkpoint_model(checkpoint_id, dest_path)

    async def list_checkpoints(self, path):
        """ list checkpoints for a given path
        """
        # 去除路径开头和结尾的斜杠
        path = path.strip("/")

        # 将路径分割为父目录和文件名
        parent, name = ("/" + path).rsplit("/", 1)
        parent = parent.strip("/")

        basename, ext = os.path.splitext(name)

        # 获取父目录的操作系统路径
        os_path = self._get_os_path(path=parent)

        # 构建检查点目录路径
        cp_dir = os.path.join(os_path, self.checkpoint_dir)

        # 如果父目录不可写，则使用系统临时目录
        if not os.access(os.path.dirname(cp_dir), os.W_OK):
            # 计算相对路径
            rel = os.path.relpath(os_path, start=self.root_dir)
            # 在系统临时目录中创建检查点目录
            cp_dir = os.path.join(tempfile.gettempdir(), "jupyter_checkpoints", rel)

        # 使用权限上下文管理器确保目录存在
        with self.perm_to_403():
            ensure_dir_exists(cp_dir)

        # list all checkpoints related with the given path
        checkpoints_under_dir = os.listdir(cp_dir)
        # filter checkpoints by path, filename is saved as f"{basename}-{checkpoint_id}{ext}"
        # where basename is the basename of the path, checkpoint_id is the checkpoint id, ext is the extension of the path
        checkpoints = []

        pattern = re.compile(f"^{re.escape(basename)}-([^\\.]+){re.escape(ext)}$")

        for filename in checkpoints_under_dir:
            is_match = pattern.match(filename)
            if is_match:
                checkpoint_id = is_match.group(1)
                checkpoints.append(
                    await self.checkpoint_model(
                        checkpoint_id,
                        os.path.join(cp_dir, filename)
                    )
                )

        # sort from old to new
        checkpoints.sort(key=lambda x: x["last_modified"])

        # if exceed max checkpoints, delete the old checkpoints
        if len(checkpoints) > self.max_checkpoints:
            for checkpoint in checkpoints[:len(checkpoints) - self.max_checkpoints]:
                await self.delete_checkpoint(checkpoint["id"], path)

            # only keep the latest max_checkpoints checkpoints
            checkpoints = checkpoints[len(checkpoints) - self.max_checkpoints:]

        # return checkpoints from old to new
        return checkpoints

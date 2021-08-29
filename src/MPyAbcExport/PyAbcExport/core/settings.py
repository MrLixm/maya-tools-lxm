import logging
from abc import abstractproperty

logger = logging.getLogger("abcex.core.settings")


class BaseArgument(object):
    @abstractproperty
    def arg_repr(self):
        """
        Returns:
            str:
        """
        pass


class FrameRange(BaseArgument):

    def __init__(self, parent):

        self.data = {
            "start": 1,
            "stop": 100,
            "step": 1.0,
            "frs": []
        }
        return

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent_value):

        if isinstance(parent_value, FrameRange):
            parent_value.add_child(self)

        self._parent = parent_value
        return

    def add_child(self, children):
        pass

    @property
    def is_subframerange(self):
        """
        Return True if this instance is not an unique frame range.
        True meaning its parent is a FrameRange instance.

        Returns:
            bool:
        """
        return isinstance(self.parent, FrameRange)

    @property
    def start(self):
        """
        Returns:
            int: start frame
        """
        return self.data["start"]

    @start.setter
    def start(self, start_value):
        """
        Args:
            start_value(int):
        """

        # check before set
        if self.is_subframerange:
            logger.error(
                "[FrameRange][start.setter] This instance has a FrameRange "
                "as parent: you cannnot set the start value with <{}>"
                "".format(start_value)
            )
            return

        self.data["start"] = int(start_value)
        return

    @property
    def stop(self):
        return self._stop

    def as_jobarg(self):
        pass


class ExportSettings(object):

    def __init__(self):

        self.data = {
            "filepath": "",
            "framerange": FrameRange(self)
        }

        return

    @property
    def filepath(self):
        """
        Returns:
            str: path to the alembic file. Ex: "C:/dir/file.abc"
        """
        output = self.data["filepath"]
        output = output.replace("$FSTART", str(self.framerange.start))
        output = output.replace("$FSTOP", str(self.framerange.stop))
        output = output.replace("$STEP", str(self.framerange.step))
        return output

    @filepath.setter
    def filepath(self, filepath_value):
        """
        Args:
            filepath_value(str):
                Path to the alembic file with the extension.

                This path can contain the following tokens:
                - $FSTART : replaced by the start frame
                - $FSTOP : replace by the stop frame
                - $STEP :  replace by the frame step

        """
        self.data["filepath"] = filepath_value
        return

    @property
    def framerange(self):
        """
        Returns:
            FrameRange: FrameRange instance
        """
        return self.data["framerange"]

    def get_as_jobarg(self):
        """
        Returns:
            str: properly formatted string for the j argument on the cmds.AbcExport command
        """

        output = list()
        for arg in self.data.items():
            output.append(arg.arg_repr)

        return " ".join(output)

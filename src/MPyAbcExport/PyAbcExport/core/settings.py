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


class FrameRangeArg(BaseArgument):

    def __init__(self, parent):
        """
        Utility class to define a frame range to export.
        Should be parented to an ExportSettings or an other FrameRangeArg.

        Args:
            parent(FrameRangeArg or ExportSettings):
             If the parent is of type FrameRangeArg, this mean this instance
              will be a subframerange to aditionally export.
        """

        self._parent = None
        self.child = None
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

        if isinstance(parent_value, FrameRangeArg):
            parent_value.add_child(self)
            self.start = parent_value.start + 1

        self._parent = parent_value
        return

    def add_child(self, child):
        """
        Args:
            child(FrameRange):
                FrameRange instances that have this instance as parent
        """
        self.child = child
        return

    @property
    def is_subframerange(self):
        """
        Return True if this instance is not an unique frame range.
        True meaning its parent is a FrameRangeArg instance.

        Returns:
            bool:
        """
        return isinstance(self.parent, FrameRangeArg)

    @property
    def frame_relative_sample(self):
        """
        Returns:
            list of float:
        """
        return self.data["frs"]

    @frame_relative_sample.setter
    def frame_relative_sample(self, frame_relative_sample_value):
        """
        Args:
            frame_relative_sample_value(list of float):
                list of frame samples, len==2 or 3
        Raises:
            TypeError: if the argument passed has incorrect values.
        """

        # value checkup
        first_value = frame_relative_sample_value[0]
        second_value = frame_relative_sample_value[1]
        if first_value > second_value:
            raise TypeError(
                "The given frame_relative_sample_value <{}> is not valid:"
                "first value is bigger than second one"
                "".format(frame_relative_sample_value)
            )

        self.data["frs"] = frame_relative_sample_value
        return

    @property
    def start(self):
        """
        Returns:
            int: frame at which the frame range is starting.
        """
        return self.data["start"]

    @start.setter
    def start(self, start_value):
        """
        Args:
            start_value(int): frame at which the frame range should start.
        """

        # check before set
        if self.is_subframerange:
            logger.error(
                "[FrameRangeArg][start.setter] This instance has a FrameRangeArg "
                "as parent: you cannnot set the start value with <{}>"
                "".format(start_value)
            )
            return

        self.data["start"] = int(start_value)
        return

    @property
    def stop(self):
        """
        Returns:
            int: frame at which the frame range is stopping.
        """
        return self.data["stop"]

    @stop.setter
    def stop(self, stop_value):
        """
        Args:
            stop_value(int): frame at which the frame range should stop.
                Must be bigger than the start frame.

        Raises:
            TypeError: if the argument is smaller than the start frame.
        """
        stop_value = int(stop_value)
        if stop_value < self.start:
            raise TypeError(
                "The given stop value <{}> is smaller than the start value <{}>"
                "".format(stop_value, self.start)
            )

        self.data["stop"] = stop_value
        return

    @property
    def step(self):
        return self.data["step"]

    @step.setter
    def step(self, step_value):
        # TODO
        self.data["step"] = step_value

    @property
    def arg_repr(self):

        outputv = (
            "-frameRange {} {} -step {}"
            "".format(self.start, self.stop, self.step)
        )
        if self.frame_relative_sample:
            outputv = (
                "{} -frameRelativeSample {}"
                " -frameRelativeSample {}"
                " -frameRelativeSample {}"
                "".format(
                    outputv,
                    self.frame_relative_sample[0],
                    self.frame_relative_sample[1],
                    self.frame_relative_sample[2]
                )
            )

        return outputv


class FilepathArg(BaseArgument):

    def __init__(self, parent):
        """

        Args:
            parent(ExportSettings):
        """
        self._value = ""
        self.parent = parent

    @property
    def arg_repr(self):
        return "-file {}".format(self.value)

    @property
    def value(self):
        """
        Returns:
            str: path to the alembic file. Ex: "C:/dir/file.abc"
        """
        output = self._value
        output = output.replace("$FSTART", str(self.parent.framerange.start))
        output = output.replace("$FSTOP", str(self.parent.framerange.stop))
        output = output.replace("$STEP", str(self.parent.framerange.step))
        return output

    @value.setter
    def value(self, filepath):
        """
        Args:
            filepath(str):
                Path to the alembic file with the extension.

                This path can contain the following tokens:
                - $FSTART : replaced by the start frame
                - $FSTOP : replace by the stop frame
                - $STEP :  replace by the frame step

        """
        self._value = filepath
        return


class ExportSettings(object):

    def __init__(self):

        self.data = {
            "filepath": FilepathArg(self),
            "framerange": FrameRangeArg(self)
        }

        return

    @property
    def filepath(self):
        """
        Returns:
            str: path to the alembic file. Ex: "C:/dir/file.abc"
        """
        outputv = self.data["filepath"]
        return outputv.value

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
        inputv = FilepathArg(self)
        inputv.value = filepath_value
        self.data["filepath"] = inputv
        return

    @property
    def framerange(self):
        """
        Returns:
            FrameRangeArg: FrameRange instance
        """
        return self.data["framerange"]

    def get_as_jobarg(self):
        """
        Returns:
            str: properly formatted string for the `j` argument on
             the cmds.AbcExport command.
        """

        output = list()
        for arg in self.data.items():
            output.append(arg.arg_repr)

        return " ".join(output)

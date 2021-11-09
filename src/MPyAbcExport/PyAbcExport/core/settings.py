import logging
from abc import abstractproperty

logger = logging.getLogger("abcex.core.settings")


class BaseArgument(object):
    @abstractproperty
    def arg_repr(self):
        """
        Flatten the class to the maya AbcExport command it correspond to.

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
        }  # default values are defined here
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
        return

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

    def __init__(self, parent, filepath=None):
        """
        Class that only hold the export path of an alembic file.
        Allowing it to have dynamic tokens.

        Correspond to the -file argument

        Args:
            parent(ExportSettings): ExportSettings object
            filepath(str or None):
                Path to the alembic file with the extension.

                Make sure the path is correctly formed before.

                This path can contain the following tokens:
                - $FSTART : replaced by the start frame
                - $FSTOP : replace by the stop frame
                - $STEP :  replace by the frame step

        """
        self._value = ""
        self.parent = parent

        if filepath:
            self.value = filepath

        return

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

                Make sure the path is correctly formed before.

                This path can contain the following tokens:
                - $FSTART : replaced by the start frame
                - $FSTOP : replace by the stop frame
                - $STEP :  replace by the frame step

        """
        self._value = filepath
        return


class AttrsArg(BaseArgument):

    arg_name = "attr"

    def __init__(self, parent, attributes=None):
        """
        Utility class to define a list of names of attributes to export.
        Should be parented to an ExportSettings.

        Args:
            parent(ExportSettings): not used for now
            attributes(str or list or None): single attribute name or an
                iterable object of them (it call extend() instead).
        """

        self._parent = None
        self.attributes = []
        if attributes:
            self.add(attributes=attributes)
        return

    def add(self, attributes):
        """
        Add the given attribute(s) name to the list of attribute to export.
        Args:
            attributes(str or list): a single attribute name or an
                iterable object of them (it call extend() instead).
        """
        if isinstance(attributes, str):
            self.attributes.append(attributes)
        else:
            self.attributes.extend(attributes)
        return

    @property
    def arg_repr(self):

        output = list()
        for attr in self.attributes:
            output.append("-{} {}".format(self.arg_name, attr))

        return " ".join(output)  # format to string before return


class AttrsPrefixArg(AttrsArg):
    """
    Same as the subclass but correspond to the attrPrefix option that export
    all the attributes having the given prefix.
    """

    arg_name = "attrPrefix"


class ExportSettings(object):

    def __init__(self):
        """
        Class holding all the argument required to export an alembic.
        Calling <arg_repr> return the flattened representation of the class
        and its children for the maya AbcExport command.

        """

        # values can only be subclass of BaseArgument /!\
        self.data = {
            "filepath": FilepathArg(self),
            "framerange": FrameRangeArg(self),
            "attributes": AttrsArg(self)
        }

        return

    @property
    def attributes(self):
        return self.data["attributes"]

    @attributes.setter
    def attributes(self, attributes_value):
        if not isinstance(attributes_value, AttrsArg):
            attributes_value = AttrsArg(self, attributes_value)
        self.data["attributes"] = attributes_value
        return

    @property
    def filepath(self):
        """
        Returns:
            FilepathArg: path to the alembic file as a FilepathArg object.
        """
        return self.data["filepath"]

    @filepath.setter
    def filepath(self, filepath_object):
        """
        Args:
            filepath_object(str or FilepathArg):
                Path to the alembic file with the extension.
                As a string or an already processed FilepathArg object.

                Make sure the path is correctly formed before.

                This path can contain the following tokens:
                - $FSTART : replaced by the start frame
                - $FSTOP : replace by the stop frame
                - $STEP :  replace by the frame step

        """
        if not isinstance(filepath_object, FilepathArg):
            filepath_object = FilepathArg(self, filepath_object)
        self.data["filepath"] = filepath_object
        return

    @property
    def framerange(self):
        """
        Returns:
            FrameRangeArg: FrameRange instance
        """
        return self.data["framerange"]

    def arg_repr(self):
        """
        Returns:
            str: properly formatted string for the `j` argument on
             the cmds.AbcExport command.
        """

        output = list()
        for arg in self.data.items():
            output.append(arg.arg_repr)

        return " ".join(output)  # format to string before return

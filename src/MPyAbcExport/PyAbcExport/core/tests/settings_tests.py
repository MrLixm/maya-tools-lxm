"""

"""


def test01():

    exs = ExportSettings()
    exs.filepath = "C:\\temp.$FSTART.abc"  # with token
    exs.filepath = "C:\\temp.abc"
    exs.attr = ["myAttribute01", "myOtherAttribute"]
    exs.attr_prefix = ["xgen", "abc_"]
    exs.no_normals = True

    # bool: true to strip namespace, int or None: number of namespace to remove at maximum on a node name
    exs.strip_namespaces = [True, None]

    exs.uv_write = True
    exs.write_face_sets = True
    exs.world_space = True
    exs.write_visibility = True

    exs.framerange.start = 1001
    exs.framerange.stop = 1069

    fr02 = FrameRange(parent=exs.framerange)
    fr02.stop = 1068  # this raise a TypeError as  fr02.start=1070
    fr02.stop = 1088
    fr02.step = 0.5

    fr03 = FrameRange(parent=fr02)
    fr03.stop = 1100
    fr03.step = 1.0  # not usefull
    fr03.frame_relative_sample = [-0.25, 0, 0.25]

    command = exs.arg_repr

    return
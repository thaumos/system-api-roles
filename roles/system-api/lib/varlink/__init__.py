
import parser


def type(typestring):
    return parser.read_type(typestring)


def interface(description):
    return parser.read_interface(description)


def load(vtype, value):
    if isinstance(vtype, str):
        vtype = parser.read_type(vtype)

    return vtype.load(value)

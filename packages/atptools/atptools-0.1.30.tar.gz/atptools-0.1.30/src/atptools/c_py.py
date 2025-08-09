import _ctypes


def di(obj_id):
    """Inverse of id() function."""
    return _ctypes.PyObj_FromPtr(obj_id)

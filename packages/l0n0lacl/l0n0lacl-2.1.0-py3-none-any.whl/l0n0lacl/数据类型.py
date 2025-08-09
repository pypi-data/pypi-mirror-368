import acl
import numpy as np

class acl数据类型:
    ACL_DT_UNDEFINED = -1  # 未知数据类型，默认值
    ACL_FLOAT = 0
    ACL_FLOAT16 = 1
    ACL_INT8 = 2
    ACL_INT32 = 3
    ACL_UINT8 = 4
    ACL_INT16 = 6
    ACL_UINT16 = 7
    ACL_UINT32 = 8
    ACL_INT64 = 9
    ACL_UINT64 = 10
    ACL_DOUBLE = 11
    ACL_BOOL = 12
    ACL_STRING = 13
    ACL_COMPLEX64 = 16
    ACL_COMPLEX128 = 17
    ACL_BF16 = 27
    ACL_INT4 = 29
    ACL_UINT1 = 30
    ACL_COMPLEX32 = 33

    @staticmethod
    def 获取类型大小(dtype: int) -> int:
        return acl.data_type_size(dtype)


def 将numpy类型转换为acl类型(numpy_dtype):
    if numpy_dtype == np.float32:
        return acl数据类型.ACL_FLOAT
    if numpy_dtype == np.float16:
        return acl数据类型.ACL_FLOAT16
    if numpy_dtype == np.int8:
        return acl数据类型.ACL_INT8
    if numpy_dtype == np.int32:
        return acl数据类型.ACL_INT32
    if numpy_dtype == np.uint8:
        return acl数据类型.ACL_UINT8
    if numpy_dtype == np.int16:
        return acl数据类型.ACL_INT16
    if numpy_dtype == np.uint16:
        return acl数据类型.ACL_UINT16
    if numpy_dtype == np.uint32:
        return acl数据类型.ACL_UINT32
    if numpy_dtype == np.int64:
        return acl数据类型.ACL_INT64
    if numpy_dtype == np.uint64:
        return acl数据类型.ACL_UINT64
    if numpy_dtype == np.double:
        return acl数据类型.ACL_DOUBLE
    if numpy_dtype == np.bool_:
        return acl数据类型.ACL_BOOL
    if numpy_dtype == np.complex64:
        return acl数据类型.ACL_COMPLEX64
    if numpy_dtype == np.complex128:
        return acl数据类型.ACL_COMPLEX128
    raise Exception(f"不支持的类型{numpy_dtype}")

def 将acl类型转换为numpy类型(acl_dtype):
    if acl_dtype == acl数据类型.ACL_FLOAT:
        return np.float32
    if acl_dtype == acl数据类型.ACL_FLOAT16:
        return np.float16
    if acl_dtype == acl数据类型.ACL_INT8:
        return np.int8
    if acl_dtype == acl数据类型.ACL_INT32:
        return np.int32
    if acl_dtype == acl数据类型.ACL_UINT8:
        return np.uint8
    if acl_dtype == acl数据类型.ACL_INT16:
        return np.int16
    if acl_dtype == acl数据类型.ACL_UINT16:
        return np.uint16
    if acl_dtype == acl数据类型.ACL_UINT32:
        return np.uint32
    if acl_dtype == acl数据类型.ACL_INT64:
        return np.int64
    if acl_dtype == acl数据类型.ACL_UINT64:
        return np.uint64
    if acl_dtype == acl数据类型.ACL_DOUBLE:
        return np.float64
    if acl_dtype == acl数据类型.ACL_BOOL:
        return np.bool_
    if acl_dtype == acl数据类型.ACL_COMPLEX64:
        return np.complex64
    if acl_dtype == acl数据类型.ACL_COMPLEX128:
        return np.complex128
    raise Exception(f"不支持的类型{acl_dtype}")

def 将numpy类型转换为torch类型(numpy_dtype):
    import torch  # type: ignore
    if numpy_dtype == np.float32:
        return torch.float32
    if numpy_dtype == np.float16:
        return torch.float16
    if numpy_dtype == np.int8:
        return torch.int8
    if numpy_dtype == np.int32:
        return torch.int32
    if numpy_dtype == np.uint8:
        return torch.uint8
    if numpy_dtype == np.int16:
        return torch.int16
    if numpy_dtype == np.uint16:
        return torch.int16
    if numpy_dtype == np.uint32:
        return torch.int32
    if numpy_dtype == np.int64:
        return torch.int64
    if numpy_dtype == np.uint64:
        return torch.int64
    if numpy_dtype == np.double:
        return torch.double
    if numpy_dtype == np.bool_:
        return torch.bool
    if numpy_dtype == np.complex64:
        return torch.complex64
    if numpy_dtype == np.complex128:
        return torch.complex128
    if numpy_dtype == np.complex_:
        return torch.complex32
    raise Exception(f"不支持的类型{numpy_dtype}")

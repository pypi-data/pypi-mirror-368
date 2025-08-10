
#ifndef E_MATH_TYPE_HPP
#define E_MATH_TYPE_HPP

// stdlib
#include <limits>
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>


bool pyobject_to_c_bool(PyObject *py)
{
    return PyObject_IsTrue(py);
}


double pyobject_to_c_double(PyObject *py)
{
    return PyFloat_AsDouble(py);
}


float pyobject_to_c_float(PyObject *py)
{
    return (float)PyFloat_AsDouble(py);
}


int8_t pyobject_to_c_int8_t(PyObject *py)
{
    auto result = PyLong_AsLong(py);
    if (result < (long)std::numeric_limits<int8_t>::lowest() ||
        result > (long)std::numeric_limits<int8_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to int8_t", py);
        return -1;
    }
    return (int8_t)result;
}


uint8_t pyobject_to_c_uint8_t(PyObject *py)
{
    auto result = PyLong_AsUnsignedLong(py);
    if (result > (unsigned long)std::numeric_limits<uint8_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to uint8_t", py);
        return -1;
    }
    return (uint8_t)result;
}


int16_t pyobject_to_c_int16_t(PyObject *py)
{
    auto result = PyLong_AsLong(py);
    if (result < (long)std::numeric_limits<int16_t>::lowest() ||
        result > (long)std::numeric_limits<int16_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to int16_t", py);
        return -1;
    }
    return (int16_t)result;
}


uint16_t pyobject_to_c_uint16_t(PyObject *py)
{
    auto result = PyLong_AsUnsignedLong(py);
    if (result > (unsigned long)std::numeric_limits<uint16_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to uint16_t", py);
        return -1;
    }
    return (uint16_t)result;
}


int32_t pyobject_to_c_int32_t(PyObject *py)
{
    auto result = PyLong_AsLong(py);
    if (result < (long)std::numeric_limits<int32_t>::lowest() ||
        result > (long)std::numeric_limits<int32_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to int32_t", py);
        return -1;
    }
    return (int32_t)result;
}


uint32_t pyobject_to_c_uint32_t(PyObject *py)
{
    auto result = PyLong_AsUnsignedLong(py);
    if (result > (unsigned long)std::numeric_limits<uint32_t>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to uint32_t", py);
        return -1;
    }
    return (uint32_t)result;
}


int pyobject_to_c_int(PyObject *py)
{
    auto result = PyLong_AsLong(py);
    if (result < (long)std::numeric_limits<int>::lowest() ||
        result > (long)std::numeric_limits<int>::max())
    {
        PyErr_Format(PyExc_OverflowError, "can't convert %R to int", py);
        return -1;
    }
    return (int)result;
}


unsigned int pyobject_to_c_unsigned_int(PyObject *py)
{
    auto result = PyLong_AsUnsignedLong(py);
    if (result > (unsigned long)std::numeric_limits<unsigned int>::max())
    {
        PyErr_Format(
            PyExc_OverflowError,
            "can't convert %R to unsigned int",
            py
        );
        return -1;
    }
    return (unsigned int)result;
}


int64_t pyobject_to_c_int64_t(PyObject *py)
{
    if (sizeof(int64_t) > sizeof(long))
    {
        auto result = PyLong_AsLongLong(py);
        if (result < (long long)std::numeric_limits<int64_t>::lowest() ||
            result > (long long)std::numeric_limits<int64_t>::max())
        {
            PyErr_Format(
                PyExc_OverflowError,
                "can't convert %R to int64_t",
                py
            );
            return -1;
        }
        return (int64_t)result;
    }
    else
    {
        auto result = PyLong_AsLong(py);
        if (result < (long)std::numeric_limits<int64_t>::lowest() ||
            result > (long)std::numeric_limits<int64_t>::max())
        {
            PyErr_Format(
                PyExc_OverflowError,
                "can't convert %R to int64_t",
                py
            );
            return -1;
        }
        return (int64_t)result;
    }
}


uint64_t pyobject_to_c_uint64_t(PyObject *py)
{
    if (sizeof(uint64_t) > sizeof(unsigned long))
    {
        auto result = PyLong_AsUnsignedLongLong(py);
        if (result > (unsigned long long)std::numeric_limits<uint64_t>::max())
        {
            PyErr_Format(
                PyExc_OverflowError,
                "can't convert %R to uint64_t",
                py
            );
            return -1;
        }
        return (uint64_t)result;
    }
    else
    {
        auto result = PyLong_AsUnsignedLong(py);
        if (result > (unsigned long)std::numeric_limits<uint64_t>::max())
        {
            PyErr_Format(
                PyExc_OverflowError,
                "can't convert %R to uint64_t",
                py
            );
            return -1;
        }
        return (uint64_t)result;
    }
}


PyObject *c_bool_to_pyobject(bool c)
{
    return PyBool_FromLong(c);
}


PyObject *c_double_to_pyobject(double c)
{
    return PyFloat_FromDouble(c);
}


PyObject *c_float_to_pyobject(float c)
{
    return PyFloat_FromDouble(c);
}


PyObject *c_int8_t_to_pyobject(int8_t c)
{
    return PyLong_FromLong(c);
}


PyObject *c_uint8_t_to_pyobject(uint8_t c)
{
    return PyLong_FromUnsignedLong(c);
}


PyObject *c_int16_t_to_pyobject(int16_t c)
{
    return PyLong_FromLong(c);
}


PyObject *c_uint16_t_to_pyobject(uint16_t c)
{
    return PyLong_FromUnsignedLong(c);
}


PyObject *c_int32_t_to_pyobject(int32_t c)
{
    return PyLong_FromLong(c);
}


PyObject *c_uint32_t_to_pyobject(uint32_t c)
{
    return PyLong_FromUnsignedLong(c);
}


PyObject *c_int_to_pyobject(int c)
{
    return PyLong_FromLong(c);
}


PyObject *c_unsigned_int_to_pyobject(unsigned int c)
{
    return PyLong_FromUnsignedLong(c);
}

PyObject *c_int64_t_to_pyobject(int64_t c)
{
    if (sizeof(int64_t) > sizeof(long))
    {
        return PyLong_FromLongLong(c);
    }
    else
    {
        return PyLong_FromLong((long)c);
    }
}


PyObject *c_uint64_t_to_pyobject(uint64_t c)
{
    if (sizeof(uint64_t) > sizeof(unsigned long))
    {
        return PyLong_FromUnsignedLongLong(c);
    }
    else
    {
        return PyLong_FromUnsignedLong((unsigned long)c);
    }
}

#endif

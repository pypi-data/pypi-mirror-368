
// generated from codegen/templates/_quaternion.hpp

#ifndef E_MATH_DQUATERNION_HPP
#define E_MATH_DQUATERNION_HPP

// stdlib
#include <limits>
#include <functional>
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
// glm
#include <glm/glm.hpp>
#include <glm/ext.hpp>
// emath
#include "_modulestate.hpp"
#include "_matrixtype.hpp"
#include "_vectortype.hpp"
#include "_quaterniontype.hpp"
#include "_type.hpp"


static PyObject *
DQuaternion__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DQuaternion does accept any keyword arguments"
        );
        return 0;
    }

    DQuaternionGlm quat(0, 0, 0, 0);
    auto arg_count = PyTuple_GET_SIZE(args);
    switch (PyTuple_GET_SIZE(args))
    {
        case 0:
        {
            break;
        }
        case 1:
        {
            auto arg = PyTuple_GET_ITEM(args, 0);
            double arg_c = pyobject_to_c_double(arg);
            auto error_occurred = PyErr_Occurred();
            if (error_occurred){ return 0; }
            quat.w = arg_c;
            break;
        }
        case 4:
        {
            for (DQuaternionGlm::length_type i = 0; i < 4; i++)
            {
                auto arg = PyTuple_GET_ITEM(args, i);
                quat[i] = pyobject_to_c_double(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }
            break;
        }
        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to DQuaternion, expected "
                "0, 1 or 4 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    DQuaternion *self = (DQuaternion*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = new DQuaternionGlm(quat);

    return (PyObject *)self;
}


static void
DQuaternion__dealloc__(DQuaternion *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

    delete self->glm;

    PyTypeObject *type = Py_TYPE(self);
    type->tp_free(self);
    Py_DECREF(type);
}


// this is roughly copied from how python hashes tuples in 3.11
#if SIZEOF_PY_UHASH_T > 4
#define _HASH_XXPRIME_1 ((Py_uhash_t)11400714785074694791ULL)
#define _HASH_XXPRIME_2 ((Py_uhash_t)14029467366897019727ULL)
#define _HASH_XXPRIME_5 ((Py_uhash_t)2870177450012600261ULL)
#define _HASH_XXROTATE(x) ((x << 31) | (x >> 33))  /* Rotate left 31 bits */
#else
#define _HASH_XXPRIME_1 ((Py_uhash_t)2654435761UL)
#define _HASH_XXPRIME_2 ((Py_uhash_t)2246822519UL)
#define _HASH_XXPRIME_5 ((Py_uhash_t)374761393UL)
#define _HASH_XXROTATE(x) ((x << 13) | (x >> 19))  /* Rotate left 13 bits */
#endif

static Py_hash_t
DQuaternion__hash__(DQuaternion *self)
{
    Py_ssize_t len = 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (DQuaternionGlm::length_type i = 0; i < len; i++)
    {
        Py_uhash_t lane = std::hash<double>{}((*self->glm)[i]);
        acc += lane * _HASH_XXPRIME_2;
        acc = _HASH_XXROTATE(acc);
        acc *= _HASH_XXPRIME_1;
    }
    acc += len ^ (_HASH_XXPRIME_5 ^ 3527539UL);

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}


static PyObject *
DQuaternion__repr__(DQuaternion *self)
{
    PyObject *result = 0;

    PyObject *py[4] = { 0 };
    for (DQuaternionGlm::length_type i = 0; i < 4; i++)
    {
        py[i] = c_double_to_pyobject((*self->glm)[i]);
        if (!py[i]){ goto cleanup; }
    }

    result = PyUnicode_FromFormat(
        "DQuaternion(%R, %R, %R, %R)",
        py[0], py[1], py[2], py[3]
    );
cleanup:
    for (DQuaternionGlm::length_type i = 0; i < 4; i++)
    {
        Py_XDECREF(py[i]);
    }
    return result;
}


static Py_ssize_t
DQuaternion__len__(DQuaternion *self)
{
    return 4;
}


static PyObject *
DQuaternion__getitem__(DQuaternion *self, Py_ssize_t index)
{
    if (index < 0 || index > 3)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = (*self->glm)[(DQuaternionGlm::length_type)index];
    return c_double_to_pyobject(c);
}


static PyObject *
DQuaternion__richcmp__(DQuaternion *self, DQuaternion *other, int op)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_EQ:
        {
            if ((*self->glm) == (*other->glm))
            {
                Py_RETURN_TRUE;
            }
            else
            {
                Py_RETURN_FALSE;
            }
        }
        case Py_NE:
        {
            if ((*self->glm) != (*other->glm))
            {
                Py_RETURN_TRUE;
            }
            else
            {
                Py_RETURN_FALSE;
            }
        }
    }
    Py_RETURN_NOTIMPLEMENTED;
}


static PyObject *
DQuaternion__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DQuaternion_PyTypeObject;

    DQuaternionGlm quat;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        quat = (*((DQuaternion *)left)->glm) + (*((DQuaternion *)right)->glm);
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
DQuaternion__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DQuaternion_PyTypeObject;

    DQuaternionGlm quat;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        quat = (*((DQuaternion *)left)->glm) - (*((DQuaternion *)right)->glm);
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
DQuaternion__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DQuaternion_PyTypeObject;

    DQuaternionGlm quat;
    if (Py_TYPE(left) == cls)
    {
        if (Py_TYPE(right) == cls)
        {
            quat = (*((DQuaternion *)left)->glm) * (*((DQuaternion *)right)->glm);
        }
        else
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            quat = (*((DQuaternion *)left)->glm) * c_right;
        }
    }
    else
    {
        auto c_left = pyobject_to_c_double(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        quat = c_left * (*((DQuaternion *)right)->glm);
    }

    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
DQuaternion__matmul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DQuaternion_PyTypeObject;
    auto vector3_cls = module_state->DVector3_PyTypeObject;
    auto vector4_cls = module_state->DVector4_PyTypeObject;

    if (Py_TYPE(left) == cls)
    {
        if (Py_TYPE(right) == cls)
        {
            auto result = (DQuaternion *)cls->tp_alloc(cls, 0);
            if (!result){ return 0; }
            auto c_result = glm::dot(
                (*((DQuaternion *)left)->glm),
                (*((DQuaternion *)right)->glm)
            );
            return c_double_to_pyobject(c_result);
        }
        else if (Py_TYPE(right) == vector3_cls)
        {
            auto result = (DVector3 *)vector3_cls->tp_alloc(vector3_cls, 0);
            if (!result){ return 0; }
            result->glm = DVector3Glm(
                (*((DQuaternion *)left)->glm) * (((DVector3 *)right)->glm)
            );
            return (PyObject *)result;
        }
        else if (Py_TYPE(right) == vector4_cls)
        {
            auto result = (DVector4 *)vector4_cls->tp_alloc(vector4_cls, 0);
            if (!result){ return 0; }
            result->glm = DVector4Glm(
                (*((DQuaternion *)left)->glm) * (((DVector4 *)right)->glm)
            );
            return (PyObject *)result;
        }
    }
    else
    {
        if (Py_TYPE(left) == vector3_cls)
        {
            auto result = (DVector3 *)vector3_cls->tp_alloc(vector3_cls, 0);
            if (!result){ return 0; }
            result->glm = DVector3Glm(
                (((DVector3 *)left)->glm) * (*((DQuaternion *)right)->glm)
            );
            return (PyObject *)result;
        }
        else if (Py_TYPE(left) == vector4_cls)
        {
            auto result = (DVector4 *)vector4_cls->tp_alloc(vector4_cls, 0);
            if (!result){ return 0; }
            result->glm = DVector4Glm(
                (((DVector4 *)left)->glm) * (*((DQuaternion *)right)->glm)
            );
            return (PyObject *)result;
        }
    }

    Py_RETURN_NOTIMPLEMENTED;
}

static PyObject *
DQuaternion__truediv__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DQuaternion_PyTypeObject;

    DQuaternionGlm quat;
    if (Py_TYPE(left) == cls)
    {
        auto c_right = pyobject_to_c_double(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        quat = (*((DQuaternion *)left)->glm) / c_right;
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
DQuaternion__neg__(DQuaternion *self)
{
    auto cls = Py_TYPE(self);

    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(-(*self->glm));

    return (PyObject *)result;
}


static int
DQuaternion_getbufferproc(DQuaternion *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "DQuaternion is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = glm::value_ptr(*self->glm);
    view->obj = (PyObject *)self;
    view->len = sizeof(double) * 4;
    view->readonly = 1;
    view->itemsize = sizeof(double);
    view->ndim = 1;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "d";
    }
    else
    {
        view->format = 0;
    }
    if (flags & PyBUF_ND)
    {
        static Py_ssize_t shape = 4;
        view->shape = &shape;
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        view->strides = &view->itemsize;
    }
    else
    {
        view->strides = 0;
    }
    view->suboffsets = 0;
    view->internal = 0;
    Py_INCREF(self);
    return 0;
}


static PyMemberDef DQuaternion_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DQuaternion, weakreflist), READONLY},
    {0}
};


static PyObject *
DQuaternion_address(DQuaternion *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
DQuaternion_pointer(DQuaternion *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_double_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
DQuaternion_Getter_w(DQuaternion *self, void *)
{
    auto c = (*self->glm).w;
    return c_double_to_pyobject(c);
}


static PyObject *
DQuaternion_Getter_x(DQuaternion *self, void *)
{
    auto c = (*self->glm).x;
    return c_double_to_pyobject(c);
}


static PyObject *
DQuaternion_Getter_y(DQuaternion *self, void *)
{
    auto c = (*self->glm).y;
    return c_double_to_pyobject(c);
}


static PyObject *
DQuaternion_Getter_z(DQuaternion *self, void *)
{
    auto c = (*self->glm).z;
    return c_double_to_pyobject(c);
}


static PyObject *
DQuaternion_magnitude(DQuaternion *self, void *)
{
    auto magnitude = glm::length(*self->glm);
    return c_double_to_pyobject(magnitude);
}

static PyObject *
DQuaternion_euler_angles(DQuaternion *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector3_PyTypeObject;

    auto angles = glm::eulerAngles(*self->glm);
    auto *result = (DVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = angles;
    return (PyObject *)result;
}


static PyGetSetDef DQuaternion_PyGetSetDef[] = {
    {"address", (getter)DQuaternion_address, 0, 0, 0},
    {"w", (getter)DQuaternion_Getter_w, 0, 0, 0},
    {"x", (getter)DQuaternion_Getter_x, 0, 0, 0},
    {"y", (getter)DQuaternion_Getter_y, 0, 0, 0},
    {"z", (getter)DQuaternion_Getter_z, 0, 0, 0},
    {"magnitude", (getter)DQuaternion_magnitude, 0, 0, 0},
    {"pointer", (getter)DQuaternion_pointer, 0, 0, 0},
    {"euler_angles", (getter)DQuaternion_euler_angles, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static DQuaternion *
DQuaternion_inverse(DQuaternion *self, void*)
{
    auto cls = Py_TYPE(self);
    auto quat = glm::inverse(*self->glm);
    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);
    return result;
}


static DQuaternion *
DQuaternion_rotate(DQuaternion *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }

    double angle = (double)PyFloat_AsDouble(args[0]);
    if (PyErr_Occurred()){ return 0; }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto vector_cls = module_state->DVector3_PyTypeObject;
    if (Py_TYPE(args[1]) != vector_cls)
    {
        PyErr_Format(PyExc_TypeError, "expected DVector3, got %R", args[0]);
        return 0;
    }
    DVector3 *vector = (DVector3 *)args[1];

    auto quat = glm::rotate(*self->glm, angle, vector->glm);

    auto cls = Py_TYPE(self);
    auto *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);
    return result;
}


static PyObject *
DQuaternion_get_limits(DQuaternion *self, void *)
{
    auto c_min = std::numeric_limits<double>::lowest();
    auto c_max = std::numeric_limits<double>::max();
    auto py_min = c_double_to_pyobject(c_min);
    if (!py_min){ return 0; }
    auto py_max = c_double_to_pyobject(c_max);
    if (!py_max)
    {
        Py_DECREF(py_min);
        return 0;
    }
    auto result = PyTuple_New(2);
    if (!result)
    {
        Py_DECREF(py_min);
        Py_DECREF(py_max);
        return 0;
    }
    PyTuple_SET_ITEM(result, 0, py_min);
    PyTuple_SET_ITEM(result, 1, py_max);
    return result;
}


static PyObject *
DQuaternion_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(double) * 4;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->glm = new DQuaternionGlm();
    std::memcpy(result->glm, view.buf, expected_size);
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
DQuaternion_lerp(DQuaternion *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }

    auto cls = Py_TYPE(self);
    if (Py_TYPE(args[0]) != cls)
    {
        PyErr_Format(PyExc_TypeError, "%R is not DQuaternion", args[0]);
        return 0;
    }
    auto other = (DQuaternion *)args[0];

    auto c_x = pyobject_to_c_double(args[1]);
    if (PyErr_Occurred()){ return 0; }

    auto quat = glm::lerp(*self->glm, *other->glm, c_x);
    auto result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);
    return (PyObject *)result;
}


static DQuaternion *
DQuaternion_normalize(DQuaternion *self, void*)
{
    auto cls = Py_TYPE(self);
    auto quat = glm::normalize(*self->glm);
    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);
    return result;
}


static DMatrix3x3 *
DQuaternion_to_matrix3(DQuaternion *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix3x3_PyTypeObject;

    auto matrix = glm::mat3_cast(*self->glm);
    auto *result = (DMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix3x3Glm(matrix);
    return result;
}


static DMatrix4x4 *
DQuaternion_to_matrix4(DQuaternion *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x4_PyTypeObject;

    auto matrix = glm::mat4_cast(*self->glm);
    auto *result = (DMatrix4x4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x4Glm(matrix);
    return result;
}


static DQuaternion *
DQuaternion_cross(DQuaternion *self, DQuaternion *other)
{
    auto cls = Py_TYPE(self);
    if (Py_TYPE(other) != cls)
    {
        PyErr_Format(PyExc_TypeError, "%R is not DQuaternion", other);
        return 0;
    }
    auto quat = glm::cross(*self->glm, *other->glm);
    DQuaternion *result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(quat);
    return result;
}


static PyObject *
DQuaternion_get_size(DQuaternion *cls, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 4);
}


static PyObject *
DQuaternion_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->DQuaternionArray_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyMethodDef DQuaternion_PyMethodDef[] = {
    {"cross", (PyCFunction)DQuaternion_cross, METH_O, 0},
    {"to_matrix3", (PyCFunction)DQuaternion_to_matrix3, METH_NOARGS, 0},
    {"to_matrix4", (PyCFunction)DQuaternion_to_matrix4, METH_NOARGS, 0},
    {"normalize", (PyCFunction)DQuaternion_normalize, METH_NOARGS, 0},
    {"inverse", (PyCFunction)DQuaternion_inverse, METH_NOARGS, 0},
    {"rotate", (PyCFunction)DQuaternion_rotate, METH_FASTCALL, 0},
    {"lerp", (PyCFunction)DQuaternion_lerp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)DQuaternion_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)DQuaternion_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)DQuaternion_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)DQuaternion_from_buffer, METH_O | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot DQuaternion_PyType_Slots [] = {
    {Py_tp_new, (void*)DQuaternion__new__},
    {Py_tp_dealloc, (void*)DQuaternion__dealloc__},
    {Py_tp_hash, (void*)DQuaternion__hash__},
    {Py_tp_repr, (void*)DQuaternion__repr__},
    {Py_sq_length, (void*)DQuaternion__len__},
    {Py_sq_item, (void*)DQuaternion__getitem__},
    {Py_tp_richcompare, (void*)DQuaternion__richcmp__},
    {Py_nb_add, (void*)DQuaternion__add__},
    {Py_nb_subtract, (void*)DQuaternion__sub__},
    {Py_nb_multiply, (void*)DQuaternion__mul__},
    {Py_nb_matrix_multiply, (void*)DQuaternion__matmul__},
    {Py_nb_true_divide, (void*)DQuaternion__truediv__},
    {Py_nb_negative, (void*)DQuaternion__neg__},
    {Py_bf_getbuffer, (void*)DQuaternion_getbufferproc},
    {Py_tp_getset, (void*)DQuaternion_PyGetSetDef},
    {Py_tp_members, (void*)DQuaternion_PyMemberDef},
    {Py_tp_methods, (void*)DQuaternion_PyMethodDef},
    {0, 0},
};


static PyType_Spec DQuaternion_PyTypeSpec = {
    "emath.DQuaternion",
    sizeof(DQuaternion),
    0,
    Py_TPFLAGS_DEFAULT,
    DQuaternion_PyType_Slots
};


static PyTypeObject *
define_DQuaternion_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DQuaternion_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DQuaternion", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}



static PyObject *
DQuaternionArray__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DQuaternion_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DQuaternion does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (DQuaternionArray *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (DQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new DQuaternionGlm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = *(((DQuaternion*)arg)->glm);
        }
        else
        {
            Py_DECREF(self);
            PyErr_Format(
                PyExc_TypeError,
                "invalid type %R, expected %R",
                arg,
                element_cls
            );
            return 0;
        }
    }

    return (PyObject *)self;
}


static void
DQuaternionArray__dealloc__(DQuaternionArray *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

    delete self->glm;

    PyTypeObject *type = Py_TYPE(self);
    type->tp_free(self);
    Py_DECREF(type);
}


static Py_hash_t
DQuaternionArray__hash__(DQuaternionArray *self)
{
    Py_ssize_t len = self->length * 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (DQuaternionGlm::length_type j = 0; j < 4; j++)
        {
            Py_uhash_t lane = std::hash<double>{}(self->glm[i][j]);
            acc += lane * _HASH_XXPRIME_2;
            acc = _HASH_XXROTATE(acc);
            acc *= _HASH_XXPRIME_1;
        }
    }
    acc += len ^ (_HASH_XXPRIME_5 ^ 3527539UL);

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}


static PyObject *
DQuaternionArray__repr__(DQuaternionArray *self)
{
    return PyUnicode_FromFormat("DQuaternionArray[%zu]", self->length);
}


static Py_ssize_t
DQuaternionArray__len__(DQuaternionArray *self)
{
    return self->length;
}


static PyObject *
DQuaternionArray__sq_getitem__(DQuaternionArray *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DQuaternion_PyTypeObject;

    DQuaternion *result = (DQuaternion *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
DQuaternionArray__mp_getitem__(DQuaternionArray *self, PyObject *key)
{
    if (PySlice_Check(key))
    {
        Py_ssize_t start;
        Py_ssize_t stop;
        Py_ssize_t step;
        Py_ssize_t length;
        if (PySlice_GetIndicesEx(key, self->length, &start, &stop, &step, &length) != 0)
        {
            return 0;
        }
        auto cls = Py_TYPE(self);
        auto *result = (DQuaternionArray *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new DQuaternionGlm[length];
            for (DQuaternionGlm::length_type i = 0; i < length; i++)
            {
                result->glm[i] = self->glm[start + (i * step)];
            }
        }
        return (PyObject *)result;
    }
    else if (PyLong_Check(key))
    {
        auto index = PyLong_AsSsize_t(key);
        if (PyErr_Occurred()){ return 0; }
        if (index < 0)
        {
            index = (Py_ssize_t)self->length + index;
        }
        if (index < 0 || index > (Py_ssize_t)self->length - 1)
        {
            PyErr_Format(PyExc_IndexError, "index out of range");
            return 0;
        }
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto element_cls = module_state->DQuaternion_PyTypeObject;

        DQuaternion *result = (DQuaternion *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = new DQuaternionGlm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
DQuaternionArray__richcmp__(
    DQuaternionArray *self,
    DQuaternionArray *other,
    int op
)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_EQ:
        {
            if (self->length == other->length)
            {
                for (size_t i = 0; i < self->length; i++)
                {
                    if (self->glm[i] != other->glm[i])
                    {
                        Py_RETURN_FALSE;
                    }
                }
                Py_RETURN_TRUE;
            }
            else
            {
                Py_RETURN_FALSE;
            }
        }
        case Py_NE:
        {
            if (self->length != other->length)
            {
                Py_RETURN_TRUE;
            }
            else
            {
                for (size_t i = 0; i < self->length; i++)
                {
                    if (self->glm[i] != other->glm[i])
                    {
                        Py_RETURN_TRUE;
                    }
                }
                Py_RETURN_FALSE;
            }
        }
    }
    Py_RETURN_NOTIMPLEMENTED;
}


static int
DQuaternionArray__bool__(DQuaternionArray *self)
{
    return self->length ? 1 : 0;
}


static int
DQuaternionArray_getbufferproc(DQuaternionArray *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "DQuaternion is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "DQuaternion cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(double) * 4* self->length;
    view->readonly = 1;
    view->itemsize = sizeof(double);
    view->ndim = 2;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "d";
    }
    else
    {
        view->format = 0;
    }
    if (flags & PyBUF_ND)
    {
        view->shape = new Py_ssize_t[2] {
            (Py_ssize_t)self->length,
            4
        };
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        static Py_ssize_t strides[] = {
            sizeof(double) * 4,
            sizeof(double)
        };
        view->strides = &strides[0];
    }
    else
    {
        view->strides = 0;
    }
    view->suboffsets = 0;
    view->internal = 0;
    Py_INCREF(self);
    return 0;
}


static void
DQuaternionArray_releasebufferproc(DQuaternionArray *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef DQuaternionArray_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DQuaternionArray, weakreflist), READONLY},
    {0}
};


static PyObject *
DQuaternionArray_address(DQuaternionArray *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
DQuaternionArray_pointer(DQuaternionArray *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_double_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
DQuaternionArray_size(DQuaternionArray *self, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 4 * self->length);
}

static PyGetSetDef DQuaternionArray_PyGetSetDef[] = {
    {"address", (getter)DQuaternionArray_address, 0, 0, 0},
    {"pointer", (getter)DQuaternionArray_pointer, 0, 0, 0},
    {"size", (getter)DQuaternionArray_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
DQuaternionArray_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(double);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(double) * 4))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(double), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(double) * 4);

    auto *result = (DQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new DQuaternionGlm[array_length];
        std::memcpy(result->glm, view.buf, view_length);
    }
    else
    {
        result->glm = 0;
    }
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
DQuaternionArray_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->DQuaternion_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef DQuaternionArray_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)DQuaternionArray_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)DQuaternionArray_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot DQuaternionArray_PyType_Slots [] = {
    {Py_tp_new, (void*)DQuaternionArray__new__},
    {Py_tp_dealloc, (void*)DQuaternionArray__dealloc__},
    {Py_tp_hash, (void*)DQuaternionArray__hash__},
    {Py_tp_repr, (void*)DQuaternionArray__repr__},
    {Py_sq_length, (void*)DQuaternionArray__len__},
    {Py_sq_item, (void*)DQuaternionArray__sq_getitem__},
    {Py_mp_subscript, (void*)DQuaternionArray__mp_getitem__},
    {Py_tp_richcompare, (void*)DQuaternionArray__richcmp__},
    {Py_nb_bool, (void*)DQuaternionArray__bool__},
    {Py_bf_getbuffer, (void*)DQuaternionArray_getbufferproc},
    {Py_bf_releasebuffer, (void*)DQuaternionArray_releasebufferproc},
    {Py_tp_getset, (void*)DQuaternionArray_PyGetSetDef},
    {Py_tp_members, (void*)DQuaternionArray_PyMemberDef},
    {Py_tp_methods, (void*)DQuaternionArray_PyMethodDef},
    {0, 0},
};


static PyType_Spec DQuaternionArray_PyTypeSpec = {
    "emath.DQuaternionArray",
    sizeof(DQuaternionArray),
    0,
    Py_TPFLAGS_DEFAULT,
    DQuaternionArray_PyType_Slots
};


static PyTypeObject *
define_DQuaternionArray_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DQuaternionArray_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DQuaternionArray", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_DQuaternion_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DQuaternion_PyTypeObject;
}


static PyTypeObject *
get_DQuaternionArray_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DQuaternionArray_PyTypeObject;
}


static PyObject *
create_DQuaternion(const double *value)
{

    auto cls = get_DQuaternion_type();
    auto result = (DQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DQuaternionGlm(*(DQuaternionGlm *)value);
    return (PyObject *)result;
}


static PyObject *
create_DQuaternionArray(size_t length, const double *value)
{
    auto cls = get_DQuaternionArray_type();
    auto result = (DQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new DQuaternionGlm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((DQuaternionGlm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static double *
get_DQuaternion_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DQuaternion_type())
    {
        PyErr_Format(PyExc_TypeError, "expected DQuaternion, got %R", self);
        return 0;
    }
    return (double *)((DQuaternion *)self)->glm;
}


static double *
get_DQuaternionArray_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DQuaternionArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DQuaternionArray, got %R",
            self
        );
        return 0;
    }
    return (double *)((DQuaternionArray *)self)->glm;
}


static size_t
get_DQuaternionArray_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_DQuaternionArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DQuaternionArray, got %R",
            self
        );
        return 0;
    }
    return ((DQuaternionArray *)self)->length;
}

#endif

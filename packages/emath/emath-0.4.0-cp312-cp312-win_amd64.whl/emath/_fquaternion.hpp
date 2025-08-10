
// generated from codegen/templates/_quaternion.hpp

#ifndef E_MATH_FQUATERNION_HPP
#define E_MATH_FQUATERNION_HPP

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
FQuaternion__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FQuaternion does accept any keyword arguments"
        );
        return 0;
    }

    FQuaternionGlm quat(0, 0, 0, 0);
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
            float arg_c = pyobject_to_c_float(arg);
            auto error_occurred = PyErr_Occurred();
            if (error_occurred){ return 0; }
            quat.w = arg_c;
            break;
        }
        case 4:
        {
            for (FQuaternionGlm::length_type i = 0; i < 4; i++)
            {
                auto arg = PyTuple_GET_ITEM(args, i);
                quat[i] = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }
            break;
        }
        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to FQuaternion, expected "
                "0, 1 or 4 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    FQuaternion *self = (FQuaternion*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = new FQuaternionGlm(quat);

    return (PyObject *)self;
}


static void
FQuaternion__dealloc__(FQuaternion *self)
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
FQuaternion__hash__(FQuaternion *self)
{
    Py_ssize_t len = 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (FQuaternionGlm::length_type i = 0; i < len; i++)
    {
        Py_uhash_t lane = std::hash<float>{}((*self->glm)[i]);
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
FQuaternion__repr__(FQuaternion *self)
{
    PyObject *result = 0;

    PyObject *py[4] = { 0 };
    for (FQuaternionGlm::length_type i = 0; i < 4; i++)
    {
        py[i] = c_float_to_pyobject((*self->glm)[i]);
        if (!py[i]){ goto cleanup; }
    }

    result = PyUnicode_FromFormat(
        "FQuaternion(%R, %R, %R, %R)",
        py[0], py[1], py[2], py[3]
    );
cleanup:
    for (FQuaternionGlm::length_type i = 0; i < 4; i++)
    {
        Py_XDECREF(py[i]);
    }
    return result;
}


static Py_ssize_t
FQuaternion__len__(FQuaternion *self)
{
    return 4;
}


static PyObject *
FQuaternion__getitem__(FQuaternion *self, Py_ssize_t index)
{
    if (index < 0 || index > 3)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = (*self->glm)[(FQuaternionGlm::length_type)index];
    return c_float_to_pyobject(c);
}


static PyObject *
FQuaternion__richcmp__(FQuaternion *self, FQuaternion *other, int op)
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
FQuaternion__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FQuaternion_PyTypeObject;

    FQuaternionGlm quat;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        quat = (*((FQuaternion *)left)->glm) + (*((FQuaternion *)right)->glm);
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
FQuaternion__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FQuaternion_PyTypeObject;

    FQuaternionGlm quat;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        quat = (*((FQuaternion *)left)->glm) - (*((FQuaternion *)right)->glm);
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
FQuaternion__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FQuaternion_PyTypeObject;

    FQuaternionGlm quat;
    if (Py_TYPE(left) == cls)
    {
        if (Py_TYPE(right) == cls)
        {
            quat = (*((FQuaternion *)left)->glm) * (*((FQuaternion *)right)->glm);
        }
        else
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            quat = (*((FQuaternion *)left)->glm) * c_right;
        }
    }
    else
    {
        auto c_left = pyobject_to_c_float(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        quat = c_left * (*((FQuaternion *)right)->glm);
    }

    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
FQuaternion__matmul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FQuaternion_PyTypeObject;
    auto vector3_cls = module_state->FVector3_PyTypeObject;
    auto vector4_cls = module_state->FVector4_PyTypeObject;

    if (Py_TYPE(left) == cls)
    {
        if (Py_TYPE(right) == cls)
        {
            auto result = (FQuaternion *)cls->tp_alloc(cls, 0);
            if (!result){ return 0; }
            auto c_result = glm::dot(
                (*((FQuaternion *)left)->glm),
                (*((FQuaternion *)right)->glm)
            );
            return c_float_to_pyobject(c_result);
        }
        else if (Py_TYPE(right) == vector3_cls)
        {
            auto result = (FVector3 *)vector3_cls->tp_alloc(vector3_cls, 0);
            if (!result){ return 0; }
            result->glm = FVector3Glm(
                (*((FQuaternion *)left)->glm) * (((FVector3 *)right)->glm)
            );
            return (PyObject *)result;
        }
        else if (Py_TYPE(right) == vector4_cls)
        {
            auto result = (FVector4 *)vector4_cls->tp_alloc(vector4_cls, 0);
            if (!result){ return 0; }
            result->glm = FVector4Glm(
                (*((FQuaternion *)left)->glm) * (((FVector4 *)right)->glm)
            );
            return (PyObject *)result;
        }
    }
    else
    {
        if (Py_TYPE(left) == vector3_cls)
        {
            auto result = (FVector3 *)vector3_cls->tp_alloc(vector3_cls, 0);
            if (!result){ return 0; }
            result->glm = FVector3Glm(
                (((FVector3 *)left)->glm) * (*((FQuaternion *)right)->glm)
            );
            return (PyObject *)result;
        }
        else if (Py_TYPE(left) == vector4_cls)
        {
            auto result = (FVector4 *)vector4_cls->tp_alloc(vector4_cls, 0);
            if (!result){ return 0; }
            result->glm = FVector4Glm(
                (((FVector4 *)left)->glm) * (*((FQuaternion *)right)->glm)
            );
            return (PyObject *)result;
        }
    }

    Py_RETURN_NOTIMPLEMENTED;
}

static PyObject *
FQuaternion__truediv__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FQuaternion_PyTypeObject;

    FQuaternionGlm quat;
    if (Py_TYPE(left) == cls)
    {
        auto c_right = pyobject_to_c_float(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        quat = (*((FQuaternion *)left)->glm) / c_right;
    }
    else
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);

    return (PyObject *)result;
}


static PyObject *
FQuaternion__neg__(FQuaternion *self)
{
    auto cls = Py_TYPE(self);

    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(-(*self->glm));

    return (PyObject *)result;
}


static int
FQuaternion_getbufferproc(FQuaternion *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FQuaternion is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = glm::value_ptr(*self->glm);
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 4;
    view->readonly = 1;
    view->itemsize = sizeof(float);
    view->ndim = 1;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "f";
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


static PyMemberDef FQuaternion_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FQuaternion, weakreflist), READONLY},
    {0}
};


static PyObject *
FQuaternion_address(FQuaternion *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
FQuaternion_pointer(FQuaternion *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FQuaternion_Getter_w(FQuaternion *self, void *)
{
    auto c = (*self->glm).w;
    return c_float_to_pyobject(c);
}


static PyObject *
FQuaternion_Getter_x(FQuaternion *self, void *)
{
    auto c = (*self->glm).x;
    return c_float_to_pyobject(c);
}


static PyObject *
FQuaternion_Getter_y(FQuaternion *self, void *)
{
    auto c = (*self->glm).y;
    return c_float_to_pyobject(c);
}


static PyObject *
FQuaternion_Getter_z(FQuaternion *self, void *)
{
    auto c = (*self->glm).z;
    return c_float_to_pyobject(c);
}


static PyObject *
FQuaternion_magnitude(FQuaternion *self, void *)
{
    auto magnitude = glm::length(*self->glm);
    return c_float_to_pyobject(magnitude);
}

static PyObject *
FQuaternion_euler_angles(FQuaternion *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector3_PyTypeObject;

    auto angles = glm::eulerAngles(*self->glm);
    auto *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = angles;
    return (PyObject *)result;
}


static PyGetSetDef FQuaternion_PyGetSetDef[] = {
    {"address", (getter)FQuaternion_address, 0, 0, 0},
    {"w", (getter)FQuaternion_Getter_w, 0, 0, 0},
    {"x", (getter)FQuaternion_Getter_x, 0, 0, 0},
    {"y", (getter)FQuaternion_Getter_y, 0, 0, 0},
    {"z", (getter)FQuaternion_Getter_z, 0, 0, 0},
    {"magnitude", (getter)FQuaternion_magnitude, 0, 0, 0},
    {"pointer", (getter)FQuaternion_pointer, 0, 0, 0},
    {"euler_angles", (getter)FQuaternion_euler_angles, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static FQuaternion *
FQuaternion_inverse(FQuaternion *self, void*)
{
    auto cls = Py_TYPE(self);
    auto quat = glm::inverse(*self->glm);
    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);
    return result;
}


static FQuaternion *
FQuaternion_rotate(FQuaternion *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }

    float angle = (float)PyFloat_AsDouble(args[0]);
    if (PyErr_Occurred()){ return 0; }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto vector_cls = module_state->FVector3_PyTypeObject;
    if (Py_TYPE(args[1]) != vector_cls)
    {
        PyErr_Format(PyExc_TypeError, "expected FVector3, got %R", args[0]);
        return 0;
    }
    FVector3 *vector = (FVector3 *)args[1];

    auto quat = glm::rotate(*self->glm, angle, vector->glm);

    auto cls = Py_TYPE(self);
    auto *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);
    return result;
}


static PyObject *
FQuaternion_get_limits(FQuaternion *self, void *)
{
    auto c_min = std::numeric_limits<float>::lowest();
    auto c_max = std::numeric_limits<float>::max();
    auto py_min = c_float_to_pyobject(c_min);
    if (!py_min){ return 0; }
    auto py_max = c_float_to_pyobject(c_max);
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
FQuaternion_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float) * 4;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->glm = new FQuaternionGlm();
    std::memcpy(result->glm, view.buf, expected_size);
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
FQuaternion_lerp(FQuaternion *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }

    auto cls = Py_TYPE(self);
    if (Py_TYPE(args[0]) != cls)
    {
        PyErr_Format(PyExc_TypeError, "%R is not FQuaternion", args[0]);
        return 0;
    }
    auto other = (FQuaternion *)args[0];

    auto c_x = pyobject_to_c_float(args[1]);
    if (PyErr_Occurred()){ return 0; }

    auto quat = glm::lerp(*self->glm, *other->glm, c_x);
    auto result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);
    return (PyObject *)result;
}


static FQuaternion *
FQuaternion_normalize(FQuaternion *self, void*)
{
    auto cls = Py_TYPE(self);
    auto quat = glm::normalize(*self->glm);
    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);
    return result;
}


static FMatrix3x3 *
FQuaternion_to_matrix3(FQuaternion *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    auto matrix = glm::mat3_cast(*self->glm);
    auto *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);
    return result;
}


static FMatrix4x4 *
FQuaternion_to_matrix4(FQuaternion *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix4x4_PyTypeObject;

    auto matrix = glm::mat4_cast(*self->glm);
    auto *result = (FMatrix4x4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix4x4Glm(matrix);
    return result;
}


static FQuaternion *
FQuaternion_cross(FQuaternion *self, FQuaternion *other)
{
    auto cls = Py_TYPE(self);
    if (Py_TYPE(other) != cls)
    {
        PyErr_Format(PyExc_TypeError, "%R is not FQuaternion", other);
        return 0;
    }
    auto quat = glm::cross(*self->glm, *other->glm);
    FQuaternion *result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(quat);
    return result;
}


static PyObject *
FQuaternion_get_size(FQuaternion *cls, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 4);
}


static PyObject *
FQuaternion_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->FQuaternionArray_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyMethodDef FQuaternion_PyMethodDef[] = {
    {"cross", (PyCFunction)FQuaternion_cross, METH_O, 0},
    {"to_matrix3", (PyCFunction)FQuaternion_to_matrix3, METH_NOARGS, 0},
    {"to_matrix4", (PyCFunction)FQuaternion_to_matrix4, METH_NOARGS, 0},
    {"normalize", (PyCFunction)FQuaternion_normalize, METH_NOARGS, 0},
    {"inverse", (PyCFunction)FQuaternion_inverse, METH_NOARGS, 0},
    {"rotate", (PyCFunction)FQuaternion_rotate, METH_FASTCALL, 0},
    {"lerp", (PyCFunction)FQuaternion_lerp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)FQuaternion_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)FQuaternion_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)FQuaternion_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)FQuaternion_from_buffer, METH_O | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FQuaternion_PyType_Slots [] = {
    {Py_tp_new, (void*)FQuaternion__new__},
    {Py_tp_dealloc, (void*)FQuaternion__dealloc__},
    {Py_tp_hash, (void*)FQuaternion__hash__},
    {Py_tp_repr, (void*)FQuaternion__repr__},
    {Py_sq_length, (void*)FQuaternion__len__},
    {Py_sq_item, (void*)FQuaternion__getitem__},
    {Py_tp_richcompare, (void*)FQuaternion__richcmp__},
    {Py_nb_add, (void*)FQuaternion__add__},
    {Py_nb_subtract, (void*)FQuaternion__sub__},
    {Py_nb_multiply, (void*)FQuaternion__mul__},
    {Py_nb_matrix_multiply, (void*)FQuaternion__matmul__},
    {Py_nb_true_divide, (void*)FQuaternion__truediv__},
    {Py_nb_negative, (void*)FQuaternion__neg__},
    {Py_bf_getbuffer, (void*)FQuaternion_getbufferproc},
    {Py_tp_getset, (void*)FQuaternion_PyGetSetDef},
    {Py_tp_members, (void*)FQuaternion_PyMemberDef},
    {Py_tp_methods, (void*)FQuaternion_PyMethodDef},
    {0, 0},
};


static PyType_Spec FQuaternion_PyTypeSpec = {
    "emath.FQuaternion",
    sizeof(FQuaternion),
    0,
    Py_TPFLAGS_DEFAULT,
    FQuaternion_PyType_Slots
};


static PyTypeObject *
define_FQuaternion_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FQuaternion_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FQuaternion", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}



static PyObject *
FQuaternionArray__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FQuaternion_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FQuaternion does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (FQuaternionArray *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (FQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new FQuaternionGlm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = *(((FQuaternion*)arg)->glm);
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
FQuaternionArray__dealloc__(FQuaternionArray *self)
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
FQuaternionArray__hash__(FQuaternionArray *self)
{
    Py_ssize_t len = self->length * 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (FQuaternionGlm::length_type j = 0; j < 4; j++)
        {
            Py_uhash_t lane = std::hash<float>{}(self->glm[i][j]);
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
FQuaternionArray__repr__(FQuaternionArray *self)
{
    return PyUnicode_FromFormat("FQuaternionArray[%zu]", self->length);
}


static Py_ssize_t
FQuaternionArray__len__(FQuaternionArray *self)
{
    return self->length;
}


static PyObject *
FQuaternionArray__sq_getitem__(FQuaternionArray *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FQuaternion_PyTypeObject;

    FQuaternion *result = (FQuaternion *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
FQuaternionArray__mp_getitem__(FQuaternionArray *self, PyObject *key)
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
        auto *result = (FQuaternionArray *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new FQuaternionGlm[length];
            for (FQuaternionGlm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->FQuaternion_PyTypeObject;

        FQuaternion *result = (FQuaternion *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = new FQuaternionGlm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
FQuaternionArray__richcmp__(
    FQuaternionArray *self,
    FQuaternionArray *other,
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
FQuaternionArray__bool__(FQuaternionArray *self)
{
    return self->length ? 1 : 0;
}


static int
FQuaternionArray_getbufferproc(FQuaternionArray *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FQuaternion is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "FQuaternion cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 4* self->length;
    view->readonly = 1;
    view->itemsize = sizeof(float);
    view->ndim = 2;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "f";
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
            sizeof(float) * 4,
            sizeof(float)
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
FQuaternionArray_releasebufferproc(FQuaternionArray *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef FQuaternionArray_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FQuaternionArray, weakreflist), READONLY},
    {0}
};


static PyObject *
FQuaternionArray_address(FQuaternionArray *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
FQuaternionArray_pointer(FQuaternionArray *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FQuaternionArray_size(FQuaternionArray *self, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 4 * self->length);
}

static PyGetSetDef FQuaternionArray_PyGetSetDef[] = {
    {"address", (getter)FQuaternionArray_address, 0, 0, 0},
    {"pointer", (getter)FQuaternionArray_pointer, 0, 0, 0},
    {"size", (getter)FQuaternionArray_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
FQuaternionArray_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(float) * 4))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(float), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(float) * 4);

    auto *result = (FQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new FQuaternionGlm[array_length];
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
FQuaternionArray_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->FQuaternion_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef FQuaternionArray_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)FQuaternionArray_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)FQuaternionArray_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FQuaternionArray_PyType_Slots [] = {
    {Py_tp_new, (void*)FQuaternionArray__new__},
    {Py_tp_dealloc, (void*)FQuaternionArray__dealloc__},
    {Py_tp_hash, (void*)FQuaternionArray__hash__},
    {Py_tp_repr, (void*)FQuaternionArray__repr__},
    {Py_sq_length, (void*)FQuaternionArray__len__},
    {Py_sq_item, (void*)FQuaternionArray__sq_getitem__},
    {Py_mp_subscript, (void*)FQuaternionArray__mp_getitem__},
    {Py_tp_richcompare, (void*)FQuaternionArray__richcmp__},
    {Py_nb_bool, (void*)FQuaternionArray__bool__},
    {Py_bf_getbuffer, (void*)FQuaternionArray_getbufferproc},
    {Py_bf_releasebuffer, (void*)FQuaternionArray_releasebufferproc},
    {Py_tp_getset, (void*)FQuaternionArray_PyGetSetDef},
    {Py_tp_members, (void*)FQuaternionArray_PyMemberDef},
    {Py_tp_methods, (void*)FQuaternionArray_PyMethodDef},
    {0, 0},
};


static PyType_Spec FQuaternionArray_PyTypeSpec = {
    "emath.FQuaternionArray",
    sizeof(FQuaternionArray),
    0,
    Py_TPFLAGS_DEFAULT,
    FQuaternionArray_PyType_Slots
};


static PyTypeObject *
define_FQuaternionArray_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FQuaternionArray_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FQuaternionArray", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_FQuaternion_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FQuaternion_PyTypeObject;
}


static PyTypeObject *
get_FQuaternionArray_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FQuaternionArray_PyTypeObject;
}


static PyObject *
create_FQuaternion(const float *value)
{

    auto cls = get_FQuaternion_type();
    auto result = (FQuaternion *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FQuaternionGlm(*(FQuaternionGlm *)value);
    return (PyObject *)result;
}


static PyObject *
create_FQuaternionArray(size_t length, const float *value)
{
    auto cls = get_FQuaternionArray_type();
    auto result = (FQuaternionArray *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new FQuaternionGlm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((FQuaternionGlm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static float *
get_FQuaternion_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FQuaternion_type())
    {
        PyErr_Format(PyExc_TypeError, "expected FQuaternion, got %R", self);
        return 0;
    }
    return (float *)((FQuaternion *)self)->glm;
}


static float *
get_FQuaternionArray_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FQuaternionArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FQuaternionArray, got %R",
            self
        );
        return 0;
    }
    return (float *)((FQuaternionArray *)self)->glm;
}


static size_t
get_FQuaternionArray_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_FQuaternionArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FQuaternionArray, got %R",
            self
        );
        return 0;
    }
    return ((FQuaternionArray *)self)->length;
}

#endif

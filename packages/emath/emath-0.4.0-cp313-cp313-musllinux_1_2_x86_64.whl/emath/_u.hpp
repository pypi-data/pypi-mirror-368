
// generated from codegen/templates/_pod.hpp

#ifndef E_MATH_U_HPP
#define E_MATH_U_HPP

// stdlib
#include <limits>
#include <functional>
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
// emath
#include "_modulestate.hpp"
#include "_podtype.hpp"
#include "_type.hpp"


static PyObject *
UArray__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "U does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (UArray *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->pod = 0;
        return (PyObject *)self;
    }

    auto *self = (UArray *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->pod = new unsigned int[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        self->pod[i] = pyobject_to_c_unsigned_int(arg);
        if (PyErr_Occurred())
        {
            Py_DECREF(self);
            PyErr_Format(
                PyExc_TypeError,
                "invalid type %R, expected unsigned int",
                arg
            );
            return 0;
        }
    }

    return (PyObject *)self;
}


static void
UArray__dealloc__(UArray *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

    delete self->pod;

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
UArray__hash__(UArray *self)
{
    Py_ssize_t len = self->length;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        Py_uhash_t lane = std::hash<unsigned int>{}(self->pod[i]);
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
UArray__repr__(UArray *self)
{
    return PyUnicode_FromFormat("UArray[%zu]", self->length);
}


static Py_ssize_t
UArray__len__(UArray *self)
{
    return self->length;
}


static PyObject *
UArray__sq_getitem__(UArray *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    return c_unsigned_int_to_pyobject(self->pod[index]);
}


static PyObject *
UArray__mp_getitem__(UArray *self, PyObject *key)
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
        auto *result = (UArray *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->pod = 0;
        }
        else
        {
            result->length = length;
            result->pod = new unsigned int[length];
            for (Py_ssize_t i = 0; i < length; i++)
            {
                result->pod[i] = self->pod[start + (i * step)];
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

        return c_unsigned_int_to_pyobject(self->pod[index]);
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
UArray__richcmp__(
    UArray *self,
    UArray *other,
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
                    if (self->pod[i] != other->pod[i])
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
                    if (self->pod[i] != other->pod[i])
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
UArray__bool__(UArray *self)
{
    return self->length ? 1 : 0;
}


static int
UArray_getbufferproc(UArray *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "U is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = self->pod;
    view->obj = (PyObject *)self;
    view->len = sizeof(unsigned int) * self->length;
    view->readonly = 1;
    view->itemsize = sizeof(unsigned int);
    view->ndim = 1;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "I";
    }
    else
    {
        view->format = 0;
    }
    if (flags & PyBUF_ND)
    {
        view->shape = new Py_ssize_t[1] {
            (Py_ssize_t)self->length
        };
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


static void
UArray_releasebufferproc(UArray *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef UArray_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(UArray, weakreflist), READONLY},
    {0}
};


static PyObject *
UArray_address(UArray *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->pod);
}


static PyObject *
UArray_pointer(UArray *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_unsigned_int_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->pod);
}


static PyObject *
UArray_size(UArray *self, void *)
{
    return PyLong_FromSize_t(sizeof(unsigned int) * self->length);
}


static PyGetSetDef UArray_PyGetSetDef[] = {
    {"address", (getter)UArray_address, 0, 0, 0},
    {"pointer", (getter)UArray_pointer, 0, 0, 0},
    {"size", (getter)UArray_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
UArray_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(unsigned int);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % sizeof(unsigned int))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(unsigned int), view_length);
        return 0;
    }
    auto array_length = view_length / sizeof(unsigned int);

    auto *result = (UArray *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->pod = new unsigned int[array_length];
        std::memcpy(result->pod, view.buf, view_length);
    }
    else
    {
        result->pod = 0;
    }
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
UArray_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }

        Py_INCREF(&PyLong_Type);
        return (PyObject *)&PyLong_Type;

}


static PyMethodDef UArray_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)UArray_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)UArray_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot UArray_PyType_Slots [] = {
    {Py_tp_new, (void*)UArray__new__},
    {Py_tp_dealloc, (void*)UArray__dealloc__},
    {Py_tp_hash, (void*)UArray__hash__},
    {Py_tp_repr, (void*)UArray__repr__},
    {Py_sq_length, (void*)UArray__len__},
    {Py_sq_item, (void*)UArray__sq_getitem__},
    {Py_mp_subscript, (void*)UArray__mp_getitem__},
    {Py_tp_richcompare, (void*)UArray__richcmp__},
    {Py_nb_bool, (void*)UArray__bool__},
    {Py_bf_getbuffer, (void*)UArray_getbufferproc},
    {Py_bf_releasebuffer, (void*)UArray_releasebufferproc},
    {Py_tp_getset, (void*)UArray_PyGetSetDef},
    {Py_tp_members, (void*)UArray_PyMemberDef},
    {Py_tp_methods, (void*)UArray_PyMethodDef},
    {0, 0},
};


static PyType_Spec UArray_PyTypeSpec = {
    "emath.UArray",
    sizeof(UArray),
    0,
    Py_TPFLAGS_DEFAULT,
    UArray_PyType_Slots
};


static PyTypeObject *
define_UArray_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &UArray_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "UArray", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_UArray_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->UArray_PyTypeObject;
}


static PyObject *
create_UArray(size_t length, const unsigned int *value)
{
    auto cls = get_UArray_type();
    auto result = (UArray *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->pod = new unsigned int[length];
        for (size_t i = 0; i < length; i++)
        {
            result->pod[i] = value[i];
        }
    }
    else
    {
        result->pod = 0;
    }
    return (PyObject *)result;
}


static unsigned int *
get_UArray_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_UArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected UArray, got %R",
            self
        );
        return 0;
    }
    return ((UArray *)self)->pod;
}


static size_t
get_UArray_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_UArray_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected UArray, got %R",
            self
        );
        return 0;
    }
    return ((UArray *)self)->length;
}

#endif

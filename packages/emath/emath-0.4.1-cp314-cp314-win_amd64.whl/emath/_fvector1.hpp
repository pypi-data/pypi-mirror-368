
// generated from codegen/templates/_vector.hpp

#ifndef E_MATH_FVECTOR1_HPP
#define E_MATH_FVECTOR1_HPP

// stdlib
#include <limits>
#include <functional>
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
// glm
#include <glm/glm.hpp>
#include <glm/gtx/compatibility.hpp>
#include <glm/ext.hpp>
// emath
#include "_modulestate.hpp"
#include "_quaterniontype.hpp"
#include "_vectortype.hpp"
#include "_type.hpp"


static PyObject *
FVector1__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{

        float c_0 = 0;


    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector1 does accept any keyword arguments"
        );
        return 0;
    }
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

                c_0 = arg_c;

            break;
        }

        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to FVector1, expected "
                "0, 1 or 1 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    FVector1 *self = (FVector1*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = FVector1Glm(

            c_0

    );

    return (PyObject *)self;
}


static void
FVector1__dealloc__(FVector1 *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

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
FVector1__hash__(FVector1 *self)
{
    Py_ssize_t len = 1;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (FVector1Glm::length_type i = 0; i < len; i++)
    {
        Py_uhash_t lane = std::hash<float>{}(self->glm[i]);
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
FVector1__repr__(FVector1 *self)
{
    PyObject *result = 0;

        PyObject *py_0 = 0;



        py_0 = c_float_to_pyobject(self->glm[0]);
        if (!py_0){ goto cleanup; }

    result = PyUnicode_FromFormat(
        "FVector1("

            "%R"

        ")",

            py_0

    );
cleanup:

        Py_XDECREF(py_0);

    return result;
}


static Py_ssize_t
FVector1__len__(FVector1 *self)
{
    return 1;
}


static PyObject *
FVector1__getitem__(FVector1 *self, Py_ssize_t index)
{
    if (index < 0 || index > 0)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = self->glm[(FVector1Glm::length_type)index];
    return c_float_to_pyobject(c);
}


static PyObject *
FVector1__richcmp__(FVector1 *self, FVector1 *other, int op)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_LT:
        {
            for (FVector1Glm::length_type i = 0; i < 1; i++)
            {
                if (self->glm[i] < other->glm[i])
                {
                    Py_RETURN_TRUE;
                }
                if (self->glm[i] != other->glm[i])
                {
                    Py_RETURN_FALSE;
                }
            }
            Py_RETURN_FALSE;
        }
        case Py_LE:
        {
            for (FVector1Glm::length_type i = 0; i < 1; i++)
            {
                if (self->glm[i] < other->glm[i])
                {
                    Py_RETURN_TRUE;
                }
                if (self->glm[i] != other->glm[i])
                {
                    Py_RETURN_FALSE;
                }
            }
            Py_RETURN_TRUE;
        }
        case Py_EQ:
        {
            if (self->glm == other->glm)
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
            if (self->glm != other->glm)
            {
                Py_RETURN_TRUE;
            }
            else
            {
                Py_RETURN_FALSE;
            }
        }
        case Py_GE:
        {
            for (FVector1Glm::length_type i = 0; i < 1; i++)
            {
                if (self->glm[i] > other->glm[i])
                {
                    Py_RETURN_TRUE;
                }
                if (self->glm[i] != other->glm[i])
                {
                    Py_RETURN_FALSE;
                }
            }
            Py_RETURN_TRUE;
        }
        case Py_GT:
        {
            for (FVector1Glm::length_type i = 0; i < 1; i++)
            {
                if (self->glm[i] > other->glm[i])
                {
                    Py_RETURN_TRUE;
                }
                if (self->glm[i] != other->glm[i])
                {
                    Py_RETURN_FALSE;
                }
            }
            Py_RETURN_FALSE;
        }
    }
    Py_RETURN_NOTIMPLEMENTED;
}


static PyObject *
FVector1__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector1_PyTypeObject;

    FVector1Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector1 *)left)->glm + ((FVector1 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector1 *)left)->glm + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left + ((FVector1 *)right)->glm;
        }
    }

    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(

            vector[0]

    );

    return (PyObject *)result;
}


static PyObject *
FVector1__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector1_PyTypeObject;

    FVector1Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector1 *)left)->glm - ((FVector1 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector1 *)left)->glm - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left - ((FVector1 *)right)->glm;
        }
    }

    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(

            vector[0]

    );

    return (PyObject *)result;
}


static PyObject *
FVector1__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector1_PyTypeObject;

    FVector1Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector1 *)left)->glm * ((FVector1 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector1 *)left)->glm * c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left * ((FVector1 *)right)->glm;
        }
    }

    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(

            vector[0]

    );

    return (PyObject *)result;
}



    static PyObject *
    FVector1__matmul__(FVector1 *left, FVector1 *right)
    {
        auto cls = Py_TYPE(left);
        if (Py_TYPE(left) != Py_TYPE(right)){ Py_RETURN_NOTIMPLEMENTED; }
        auto c_result = glm::dot(left->glm, right->glm);
        return c_float_to_pyobject(c_result);
    }


    static PyObject *
    FVector1__mod__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector1_PyTypeObject;

        FVector1Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::mod(
                ((FVector1 *)left)->glm,
                ((FVector1 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(((FVector1 *)left)->glm, c_right);
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(FVector1Glm(c_left), ((FVector1 *)right)->glm);
            }
        }

        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(

                vector[0]

        );

        return (PyObject *)result;
    }


    static PyObject *
    FVector1__pow__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector1_PyTypeObject;

        FVector1Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::pow(
                ((FVector1 *)left)->glm,
                ((FVector1 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(((FVector1 *)left)->glm, FVector1Glm(c_right));
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(FVector1Glm(c_left), ((FVector1 *)right)->glm);
            }
        }

        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(

                vector[0]

        );

        return (PyObject *)result;
    }





    static PyObject *
    FVector1__truediv__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector1_PyTypeObject;

        FVector1Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {

            vector = ((FVector1 *)left)->glm / ((FVector1 *)right)->glm;
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = ((FVector1 *)left)->glm / c_right;
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = c_left / ((FVector1 *)right)->glm;
            }
        }

        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(

                vector[0]

        );

        return (PyObject *)result;
    }




    static PyObject *
    FVector1__neg__(FVector1 *self)
    {
        auto cls = Py_TYPE(self);

            FVector1Glm vector = -self->glm;


        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(

                vector[0]

        );

        return (PyObject *)result;
    }



static PyObject *
FVector1__abs__(FVector1 *self)
{
    auto cls = Py_TYPE(self);
    FVector1Glm vector = glm::abs(self->glm);

    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(

            vector[0]

    );

    return (PyObject *)result;
}


static int
FVector1__bool__(FVector1 *self)
{

        if (self->glm[0] == 0)
        {
            return 0;
        }

    return 1;
}


static int
FVector1_getbufferproc(FVector1 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FVector1 is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = &self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 1;
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
        static Py_ssize_t shape = 1;
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



    static PyObject *
    FVector1_Getter_0(FVector1 *self, void *)
    {
        auto c = self->glm[0];
        return c_float_to_pyobject(c);
    }




    static PyObject *
    FVector1_magnitude(FVector1 *self, void *)
    {
        auto magnitude = glm::length(self->glm);
        return c_float_to_pyobject(magnitude);
    }



static PyObject *
FVector1_address(FVector1 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)&self->glm);
}


static PyObject *
FVector1_pointer(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }

    auto void_p_cls = module_state->ctypes_c_void_p;
    auto void_p = PyObject_CallFunction(void_p_cls, "n", (Py_ssize_t)&self->glm);
    if (!void_p){ return 0; }

    auto c_p = module_state->ctypes_c_float_p;
    auto result = PyObject_CallFunction(module_state->ctypes_cast, "OO", void_p, c_p);
    Py_DECREF(void_p);
    return result;
}


static PyGetSetDef FVector1_PyGetSetDef[] = {
    {"address", (getter)FVector1_address, 0, 0, 0},
    {"x", (getter)FVector1_Getter_0, 0, 0, 0},
    {"r", (getter)FVector1_Getter_0, 0, 0, 0},
    {"s", (getter)FVector1_Getter_0, 0, 0, 0},
    {"u", (getter)FVector1_Getter_0, 0, 0, 0},




        {"magnitude", (getter)FVector1_magnitude, 0, 0, 0},

    {"pointer", (getter)FVector1_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};



    static PyObject *
    swizzle_2_FVector1(FVector1 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        FVector2Glm vec;
        for (int i = 0; i < 2; i++)
        {
            char c_name = attr[i];
            int glm_index;
            switch(c_name)
            {
                case 'o':
                    vec[i] = 0;
                    continue;
                case 'l':
                    vec[i] = 1;
                    continue;
                case 'x':
                case 'r':
                case 's':
                case 'u':
                    glm_index = 0;
                    break;



                default:
                {
                    PyErr_Format(
                        PyExc_AttributeError,
                        "invalid swizzle: %R", py_attr
                    );
                    return 0;
                }
            }
            vec[i] = self->glm[glm_index];
        }

        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector2_PyTypeObject;

        FVector2 *result = (FVector2 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector2Glm(vec);

        return (PyObject *)result;
    }



    static PyObject *
    swizzle_3_FVector1(FVector1 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        FVector3Glm vec;
        for (int i = 0; i < 3; i++)
        {
            char c_name = attr[i];
            int glm_index;
            switch(c_name)
            {
                case 'o':
                    vec[i] = 0;
                    continue;
                case 'l':
                    vec[i] = 1;
                    continue;
                case 'x':
                case 'r':
                case 's':
                case 'u':
                    glm_index = 0;
                    break;



                default:
                {
                    PyErr_Format(
                        PyExc_AttributeError,
                        "invalid swizzle: %R", py_attr
                    );
                    return 0;
                }
            }
            vec[i] = self->glm[glm_index];
        }

        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector3_PyTypeObject;

        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(vec);

        return (PyObject *)result;
    }



    static PyObject *
    swizzle_4_FVector1(FVector1 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        FVector4Glm vec;
        for (int i = 0; i < 4; i++)
        {
            char c_name = attr[i];
            int glm_index;
            switch(c_name)
            {
                case 'o':
                    vec[i] = 0;
                    continue;
                case 'l':
                    vec[i] = 1;
                    continue;
                case 'x':
                case 'r':
                case 's':
                case 'u':
                    glm_index = 0;
                    break;



                default:
                {
                    PyErr_Format(
                        PyExc_AttributeError,
                        "invalid swizzle: %R", py_attr
                    );
                    return 0;
                }
            }
            vec[i] = self->glm[glm_index];
        }

        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector4_PyTypeObject;

        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(vec);

        return (PyObject *)result;
    }




static PyObject *
FVector1__getattr__(FVector1 *self, PyObject *py_attr)
{
    PyObject *result = PyObject_GenericGetAttr((PyObject *)self, py_attr);
    if (result != 0){ return result; }

    auto attr_length = PyUnicode_GET_LENGTH(py_attr);
    switch(attr_length)
    {
        case 2:
        {
            PyErr_Clear();
            return swizzle_2_FVector1(self, py_attr);
        }
        case 3:
        {
            PyErr_Clear();
            return swizzle_3_FVector1(self, py_attr);
        }
        case 4:
        {
            PyErr_Clear();
            return swizzle_4_FVector1(self, py_attr);
        }
    }
    return 0;
}


static PyMemberDef FVector1_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector1, weakreflist), READONLY},
    {0}
};






    static PyObject *
    FVector1_lerp(FVector1 *self, PyObject *const *args, Py_ssize_t nargs)
    {
        if (nargs != 2)
        {
            PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
            return 0;
        }

        auto cls = Py_TYPE(self);
        if (Py_TYPE(args[0]) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector1", args[0]);
            return 0;
        }
        auto other = (FVector1 *)args[0];

        auto c_x = pyobject_to_c_float(args[1]);
        if (PyErr_Occurred()){ return 0; }


            auto vector = glm::lerp<float>(*(float *)&self->glm, *(float *)&other->glm, c_x);

        auto result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(vector);
        return (PyObject *)result;
    }


    static FVector1 *
    FVector1_normalize(FVector1 *self, void*)
    {
        auto cls = Py_TYPE(self);
        auto vector = glm::normalize(self->glm);
        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(

                vector[0]

        );
        return result;
    }

    static PyObject *
    FVector1_distance(FVector1 *self, FVector1 *other)
    {
        auto cls = Py_TYPE(self);
        if (Py_TYPE(other) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector1", other);
            return 0;
        }
        auto result = glm::distance(self->glm, other->glm);
        return c_float_to_pyobject(result);
    }




static PyObject *
FVector1_min(FVector1 *self, PyObject *min)
{
    auto c_min = pyobject_to_c_float(min);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::min(self->glm, c_min);
    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector1_max(FVector1 *self, PyObject *max)
{
    auto c_max = pyobject_to_c_float(max);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::max(self->glm, c_max);
    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector1_clamp(FVector1 *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }
    auto c_min = pyobject_to_c_float(args[0]);
    if (PyErr_Occurred()){ return 0; }
    auto c_max = pyobject_to_c_float(args[1]);
    if (PyErr_Occurred()){ return 0; }

    auto cls = Py_TYPE(self);
    auto vector = glm::clamp(self->glm, c_min, c_max);
    FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector1_get_size(FVector1 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 1);
}


static PyObject *
FVector1_get_limits(FVector1 *cls, void *)
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
FVector1_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float) * 1;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    std::memcpy(&result->glm, view.buf, expected_size);
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
FVector1_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->FVector1Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyObject *
FVector1_to_b(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->BVector1_PyTypeObject;
    auto *result = (BVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = BVector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_d(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector1_PyTypeObject;
    auto *result = (DVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_i8(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I8Vector1_PyTypeObject;
    auto *result = (I8Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I8Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_u8(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U8Vector1_PyTypeObject;
    auto *result = (U8Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U8Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_i16(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I16Vector1_PyTypeObject;
    auto *result = (I16Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I16Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_u16(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U16Vector1_PyTypeObject;
    auto *result = (U16Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U16Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_i32(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I32Vector1_PyTypeObject;
    auto *result = (I32Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I32Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_u32(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U32Vector1_PyTypeObject;
    auto *result = (U32Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U32Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_i(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->IVector1_PyTypeObject;
    auto *result = (IVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = IVector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_u(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->UVector1_PyTypeObject;
    auto *result = (UVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = UVector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_i64(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I64Vector1_PyTypeObject;
    auto *result = (I64Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I64Vector1Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector1_to_u64(FVector1 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U64Vector1_PyTypeObject;
    auto *result = (U64Vector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U64Vector1Glm(self->glm);
    return (PyObject *)result;
}



static PyMethodDef FVector1_PyMethodDef[] = {


        {"lerp", (PyCFunction)FVector1_lerp, METH_FASTCALL, 0},
        {"normalize", (PyCFunction)FVector1_normalize, METH_NOARGS, 0},
        {"distance", (PyCFunction)FVector1_distance, METH_O, 0},

    {"min", (PyCFunction)FVector1_min, METH_O, 0},
    {"max", (PyCFunction)FVector1_max, METH_O, 0},
    {"clamp", (PyCFunction)FVector1_clamp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)FVector1_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)FVector1_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)FVector1_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)FVector1_from_buffer, METH_O | METH_CLASS, 0},

        {"to_b", (PyCFunction)FVector1_to_b, METH_NOARGS, 0},

        {"to_d", (PyCFunction)FVector1_to_d, METH_NOARGS, 0},

        {"to_i8", (PyCFunction)FVector1_to_i8, METH_NOARGS, 0},

        {"to_u8", (PyCFunction)FVector1_to_u8, METH_NOARGS, 0},

        {"to_i16", (PyCFunction)FVector1_to_i16, METH_NOARGS, 0},

        {"to_u16", (PyCFunction)FVector1_to_u16, METH_NOARGS, 0},

        {"to_i32", (PyCFunction)FVector1_to_i32, METH_NOARGS, 0},

        {"to_u32", (PyCFunction)FVector1_to_u32, METH_NOARGS, 0},

        {"to_i", (PyCFunction)FVector1_to_i, METH_NOARGS, 0},

        {"to_u", (PyCFunction)FVector1_to_u, METH_NOARGS, 0},

        {"to_i64", (PyCFunction)FVector1_to_i64, METH_NOARGS, 0},

        {"to_u64", (PyCFunction)FVector1_to_u64, METH_NOARGS, 0},

    {0, 0, 0, 0}
};


static PyType_Slot FVector1_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector1__new__},
    {Py_tp_dealloc, (void*)FVector1__dealloc__},
    {Py_tp_hash, (void*)FVector1__hash__},
    {Py_tp_repr, (void*)FVector1__repr__},
    {Py_sq_length, (void*)FVector1__len__},
    {Py_sq_item, (void*)FVector1__getitem__},
    {Py_tp_richcompare, (void*)FVector1__richcmp__},
    {Py_nb_add, (void*)FVector1__add__},
    {Py_nb_subtract, (void*)FVector1__sub__},
    {Py_nb_multiply, (void*)FVector1__mul__},

        {Py_nb_matrix_multiply, (void*)FVector1__matmul__},
        {Py_nb_remainder, (void*)FVector1__mod__},
        {Py_nb_power, (void*)FVector1__pow__},


        {Py_nb_true_divide, (void*)FVector1__truediv__},


        {Py_nb_negative, (void*)FVector1__neg__},

    {Py_nb_absolute, (void*)FVector1__abs__},
    {Py_nb_bool, (void*)FVector1__bool__},
    {Py_bf_getbuffer, (void*)FVector1_getbufferproc},
    {Py_tp_getset, (void*)FVector1_PyGetSetDef},
    {Py_tp_getattro, (void*)FVector1__getattr__},
    {Py_tp_members, (void*)FVector1_PyMemberDef},
    {Py_tp_methods, (void*)FVector1_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector1_PyTypeSpec = {
    "emath.FVector1",
    sizeof(FVector1),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector1_PyType_Slots
};


static PyTypeObject *
define_FVector1_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector1_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector1", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


    static FVector1 *
    create_FVector1_from_glm(const FVector1Glm& glm)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector1_PyTypeObject;

        FVector1 *result = (FVector1 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(glm);

        return result;
    }



static PyObject *
FVector1Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector1_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector1 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (FVector1Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (FVector1Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new FVector1Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = ((FVector1*)arg)->glm;
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
FVector1Array__dealloc__(FVector1Array *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

    delete[] self->glm;

    PyTypeObject *type = Py_TYPE(self);
    type->tp_free(self);
    Py_DECREF(type);
}


static Py_hash_t
FVector1Array__hash__(FVector1Array *self)
{
    Py_ssize_t len = self->length * 1;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (FVector1Glm::length_type j = 0; j < 1; j++)
        {
            Py_uhash_t lane = std::hash<float>{}(self->glm[i][j]);
            acc += lane * _HASH_XXPRIME_2;
            acc = _HASH_XXROTATE(acc);
            acc *= _HASH_XXPRIME_1;
        }
        acc += len ^ (_HASH_XXPRIME_5 ^ 3527539UL);
    }

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}


static PyObject *
FVector1Array__repr__(FVector1Array *self)
{
    return PyUnicode_FromFormat("FVector1Array[%zu]", self->length);
}


static Py_ssize_t
FVector1Array__len__(FVector1Array *self)
{
    return self->length;
}


static PyObject *
FVector1Array__sq_getitem__(FVector1Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector1_PyTypeObject;

    FVector1 *result = (FVector1 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = FVector1Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
FVector1Array__mp_getitem__(FVector1Array *self, PyObject *key)
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
        auto *result = (FVector1Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new FVector1Glm[length];
            for (FVector1Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->FVector1_PyTypeObject;

        FVector1 *result = (FVector1 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = FVector1Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
FVector1Array__richcmp__(
    FVector1Array *self,
    FVector1Array *other,
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
FVector1Array__bool__(FVector1Array *self)
{
    return self->length ? 1 : 0;
}


static int
FVector1Array_getbufferproc(FVector1Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_BufferError, "FVector1 is read only");
        view->obj = 0;
        return -1;
    }

    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 1 * self->length;
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
            1
        };
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        static Py_ssize_t strides[] = {
            sizeof(float) * 1,
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
FVector1Array_releasebufferproc(FVector1Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef FVector1Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector1Array, weakreflist), READONLY},
    {0}
};


static PyObject *
FVector1Array_address(FVector1Array *self, void *)
{
    return PyLong_FromVoidPtr(self->glm);
}


static PyObject *
FVector1Array_pointer(FVector1Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FVector1Array_size(FVector1Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 1 * self->length);
}


static PyGetSetDef FVector1Array_PyGetSetDef[] = {
    {"address", (getter)FVector1Array_address, 0, 0, 0},
    {"pointer", (getter)FVector1Array_pointer, 0, 0, 0},
    {"size", (getter)FVector1Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
FVector1Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(float) * 1))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(float), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(float) * 1);

    auto *result = (FVector1Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new FVector1Glm[array_length];
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
FVector1Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->FVector1_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef FVector1Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)FVector1Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)FVector1Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FVector1Array_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector1Array__new__},
    {Py_tp_dealloc, (void*)FVector1Array__dealloc__},
    {Py_tp_hash, (void*)FVector1Array__hash__},
    {Py_tp_repr, (void*)FVector1Array__repr__},
    {Py_sq_length, (void*)FVector1Array__len__},
    {Py_sq_item, (void*)FVector1Array__sq_getitem__},
    {Py_mp_subscript, (void*)FVector1Array__mp_getitem__},
    {Py_tp_richcompare, (void*)FVector1Array__richcmp__},
    {Py_nb_bool, (void*)FVector1Array__bool__},
    {Py_bf_getbuffer, (void*)FVector1Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)FVector1Array_releasebufferproc},
    {Py_tp_getset, (void*)FVector1Array_PyGetSetDef},
    {Py_tp_members, (void*)FVector1Array_PyMemberDef},
    {Py_tp_methods, (void*)FVector1Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector1Array_PyTypeSpec = {
    "emath.FVector1Array",
    sizeof(FVector1Array),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector1Array_PyType_Slots
};


static PyTypeObject *
define_FVector1Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector1Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector1Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_FVector1_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector1_PyTypeObject;
}


static PyTypeObject *
get_FVector1Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector1Array_PyTypeObject;
}


static PyObject *
create_FVector1(const float *value)
{
    auto cls = get_FVector1_type();
    auto result = (FVector1 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = *(FVector1Glm *)value;
    return (PyObject *)result;
}


static PyObject *
create_FVector1Array(size_t length, const float *value)
{
    auto cls = get_FVector1Array_type();
    auto result = (FVector1Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new FVector1Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((FVector1Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static const float *
get_FVector1_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector1_type())
    {
        PyErr_Format(PyExc_TypeError, "expected FVector1, got %R", self);
        return 0;
    }
    return (float *)&((FVector1 *)self)->glm;
}


static const float *
get_FVector1Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector1Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector1Array, got %R",
            self
        );
        return 0;
    }
    return (float *)((FVector1Array *)self)->glm;
}


static size_t
get_FVector1Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector1Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector1Array, got %R",
            self
        );
        return 0;
    }
    return ((FVector1Array *)self)->length;
}

#endif

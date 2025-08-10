
// generated from codegen/templates/_vector.hpp

#ifndef E_MATH_FVECTOR3_HPP
#define E_MATH_FVECTOR3_HPP

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
FVector3__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{

        float c_0 = 0;

        float c_1 = 0;

        float c_2 = 0;


    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector3 does accept any keyword arguments"
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

                c_1 = arg_c;

                c_2 = arg_c;

            break;
        }

            case 3:
            {

                {
                    auto arg = PyTuple_GET_ITEM(args, 0);
                    c_0 = pyobject_to_c_float(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                {
                    auto arg = PyTuple_GET_ITEM(args, 1);
                    c_1 = pyobject_to_c_float(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                {
                    auto arg = PyTuple_GET_ITEM(args, 2);
                    c_2 = pyobject_to_c_float(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                break;
            }

        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to FVector3, expected "
                "0, 1 or 3 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    FVector3 *self = (FVector3*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = FVector3Glm(

            c_0,

            c_1,

            c_2

    );

    return (PyObject *)self;
}


static void
FVector3__dealloc__(FVector3 *self)
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
FVector3__hash__(FVector3 *self)
{
    Py_ssize_t len = 3;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (FVector3Glm::length_type i = 0; i < len; i++)
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
FVector3__repr__(FVector3 *self)
{
    PyObject *result = 0;

        PyObject *py_0 = 0;

        PyObject *py_1 = 0;

        PyObject *py_2 = 0;



        py_0 = c_float_to_pyobject(self->glm[0]);
        if (!py_0){ goto cleanup; }

        py_1 = c_float_to_pyobject(self->glm[1]);
        if (!py_1){ goto cleanup; }

        py_2 = c_float_to_pyobject(self->glm[2]);
        if (!py_2){ goto cleanup; }

    result = PyUnicode_FromFormat(
        "FVector3("

            "%R, "

            "%R, "

            "%R"

        ")",

            py_0,

            py_1,

            py_2

    );
cleanup:

        Py_XDECREF(py_0);

        Py_XDECREF(py_1);

        Py_XDECREF(py_2);

    return result;
}


static Py_ssize_t
FVector3__len__(FVector3 *self)
{
    return 3;
}


static PyObject *
FVector3__getitem__(FVector3 *self, Py_ssize_t index)
{
    if (index < 0 || index > 2)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = self->glm[(FVector3Glm::length_type)index];
    return c_float_to_pyobject(c);
}


static PyObject *
FVector3__richcmp__(FVector3 *self, FVector3 *other, int op)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_LT:
        {
            for (FVector3Glm::length_type i = 0; i < 3; i++)
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
            for (FVector3Glm::length_type i = 0; i < 3; i++)
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
            for (FVector3Glm::length_type i = 0; i < 3; i++)
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
            for (FVector3Glm::length_type i = 0; i < 3; i++)
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
FVector3__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector3_PyTypeObject;

    FVector3Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector3 *)left)->glm + ((FVector3 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector3 *)left)->glm + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left + ((FVector3 *)right)->glm;
        }
    }

    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(

            vector[0],

            vector[1],

            vector[2]

    );

    return (PyObject *)result;
}


static PyObject *
FVector3__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector3_PyTypeObject;

    FVector3Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector3 *)left)->glm - ((FVector3 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector3 *)left)->glm - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left - ((FVector3 *)right)->glm;
        }
    }

    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(

            vector[0],

            vector[1],

            vector[2]

    );

    return (PyObject *)result;
}


static PyObject *
FVector3__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector3_PyTypeObject;

    FVector3Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector3 *)left)->glm * ((FVector3 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector3 *)left)->glm * c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left * ((FVector3 *)right)->glm;
        }
    }

    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(

            vector[0],

            vector[1],

            vector[2]

    );

    return (PyObject *)result;
}



    static PyObject *
    FVector3__matmul__(FVector3 *left, FVector3 *right)
    {
        auto cls = Py_TYPE(left);
        if (Py_TYPE(left) != Py_TYPE(right)){ Py_RETURN_NOTIMPLEMENTED; }
        auto c_result = glm::dot(left->glm, right->glm);
        return c_float_to_pyobject(c_result);
    }


    static PyObject *
    FVector3__mod__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector3_PyTypeObject;

        FVector3Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::mod(
                ((FVector3 *)left)->glm,
                ((FVector3 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(((FVector3 *)left)->glm, c_right);
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(FVector3Glm(c_left), ((FVector3 *)right)->glm);
            }
        }

        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(

                vector[0],

                vector[1],

                vector[2]

        );

        return (PyObject *)result;
    }


    static PyObject *
    FVector3__pow__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector3_PyTypeObject;

        FVector3Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::pow(
                ((FVector3 *)left)->glm,
                ((FVector3 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(((FVector3 *)left)->glm, FVector3Glm(c_right));
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(FVector3Glm(c_left), ((FVector3 *)right)->glm);
            }
        }

        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(

                vector[0],

                vector[1],

                vector[2]

        );

        return (PyObject *)result;
    }





    static PyObject *
    FVector3__truediv__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector3_PyTypeObject;

        FVector3Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {

            vector = ((FVector3 *)left)->glm / ((FVector3 *)right)->glm;
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = ((FVector3 *)left)->glm / c_right;
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = c_left / ((FVector3 *)right)->glm;
            }
        }

        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(

                vector[0],

                vector[1],

                vector[2]

        );

        return (PyObject *)result;
    }




    static PyObject *
    FVector3__neg__(FVector3 *self)
    {
        auto cls = Py_TYPE(self);

            FVector3Glm vector = -self->glm;


        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(

                vector[0],

                vector[1],

                vector[2]

        );

        return (PyObject *)result;
    }



static PyObject *
FVector3__abs__(FVector3 *self)
{
    auto cls = Py_TYPE(self);
    FVector3Glm vector = glm::abs(self->glm);

    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(

            vector[0],

            vector[1],

            vector[2]

    );

    return (PyObject *)result;
}


static int
FVector3__bool__(FVector3 *self)
{

        if (self->glm[0] == 0)
        {
            return 0;
        }

        if (self->glm[1] == 0)
        {
            return 0;
        }

        if (self->glm[2] == 0)
        {
            return 0;
        }

    return 1;
}


static int
FVector3_getbufferproc(FVector3 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FVector3 is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = &self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 3;
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
        static Py_ssize_t shape = 3;
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
    FVector3_Getter_0(FVector3 *self, void *)
    {
        auto c = self->glm[0];
        return c_float_to_pyobject(c);
    }

    static PyObject *
    FVector3_Getter_1(FVector3 *self, void *)
    {
        auto c = self->glm[1];
        return c_float_to_pyobject(c);
    }

    static PyObject *
    FVector3_Getter_2(FVector3 *self, void *)
    {
        auto c = self->glm[2];
        return c_float_to_pyobject(c);
    }




    static PyObject *
    FVector3_magnitude(FVector3 *self, void *)
    {
        auto magnitude = glm::length(self->glm);
        return c_float_to_pyobject(magnitude);
    }



static PyObject *
FVector3_address(FVector3 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)&self->glm);
}


static PyObject *
FVector3_pointer(FVector3 *self, void *)
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


static PyGetSetDef FVector3_PyGetSetDef[] = {
    {"address", (getter)FVector3_address, 0, 0, 0},
    {"x", (getter)FVector3_Getter_0, 0, 0, 0},
    {"r", (getter)FVector3_Getter_0, 0, 0, 0},
    {"s", (getter)FVector3_Getter_0, 0, 0, 0},
    {"u", (getter)FVector3_Getter_0, 0, 0, 0},

        {"y", (getter)FVector3_Getter_1, 0, 0, 0},
        {"g", (getter)FVector3_Getter_1, 0, 0, 0},
        {"t", (getter)FVector3_Getter_1, 0, 0, 0},
        {"v", (getter)FVector3_Getter_1, 0, 0, 0},


        {"z", (getter)FVector3_Getter_2, 0, 0, 0},
        {"b", (getter)FVector3_Getter_2, 0, 0, 0},
        {"p", (getter)FVector3_Getter_2, 0, 0, 0},



        {"magnitude", (getter)FVector3_magnitude, 0, 0, 0},

    {"pointer", (getter)FVector3_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};



    static PyObject *
    swizzle_2_FVector3(FVector3 *self, PyObject *py_attr)
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

                    case 'y':
                    case 'g':
                    case 't':
                    case 'v':
                        glm_index = 1;
                        break;


                    case 'z':
                    case 'b':
                    case 'p':
                        glm_index = 2;
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
    swizzle_3_FVector3(FVector3 *self, PyObject *py_attr)
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

                    case 'y':
                    case 'g':
                    case 't':
                    case 'v':
                        glm_index = 1;
                        break;


                    case 'z':
                    case 'b':
                    case 'p':
                        glm_index = 2;
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
    swizzle_4_FVector3(FVector3 *self, PyObject *py_attr)
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

                    case 'y':
                    case 'g':
                    case 't':
                    case 'v':
                        glm_index = 1;
                        break;


                    case 'z':
                    case 'b':
                    case 'p':
                        glm_index = 2;
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
FVector3__getattr__(FVector3 *self, PyObject *py_attr)
{
    PyObject *result = PyObject_GenericGetAttr((PyObject *)self, py_attr);
    if (result != 0){ return result; }

    auto attr_length = PyUnicode_GET_LENGTH(py_attr);
    switch(attr_length)
    {
        case 2:
        {
            PyErr_Clear();
            return swizzle_2_FVector3(self, py_attr);
        }
        case 3:
        {
            PyErr_Clear();
            return swizzle_3_FVector3(self, py_attr);
        }
        case 4:
        {
            PyErr_Clear();
            return swizzle_4_FVector3(self, py_attr);
        }
    }
    return 0;
}


static PyMemberDef FVector3_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector3, weakreflist), READONLY},
    {0}
};




        static FVector3 *
        FVector3_cross(FVector3 *self, FVector3 *other)
        {
            auto cls = Py_TYPE(self);
            if (Py_TYPE(other) != cls)
            {
                PyErr_Format(PyExc_TypeError, "%R is not FVector3", other);
                return 0;
            }
            auto vector = glm::cross(self->glm, other->glm);
            FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
            if (!result){ return 0; }
            result->glm = FVector3Glm(

                    vector[0],

                    vector[1],

                    vector[2]

            );
            return result;
        }

        static FQuaternion *
        FVector3_to_quaternion(FVector3 *self, void*)
        {
            auto module_state = get_module_state();
            if (!module_state){ return 0; }
            auto cls = module_state->FQuaternion_PyTypeObject;

            auto result = (FQuaternion *)cls->tp_alloc(cls, 0);
            if (!result){ return 0; }
            result->glm = new FQuaternionGlm(self->glm);
            return result;
        }



    static PyObject *
    FVector3_lerp(FVector3 *self, PyObject *const *args, Py_ssize_t nargs)
    {
        if (nargs != 2)
        {
            PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
            return 0;
        }

        auto cls = Py_TYPE(self);
        if (Py_TYPE(args[0]) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector3", args[0]);
            return 0;
        }
        auto other = (FVector3 *)args[0];

        auto c_x = pyobject_to_c_float(args[1]);
        if (PyErr_Occurred()){ return 0; }


            auto vector = glm::lerp(self->glm, other->glm, c_x);

        auto result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(vector);
        return (PyObject *)result;
    }


    static FVector3 *
    FVector3_normalize(FVector3 *self, void*)
    {
        auto cls = Py_TYPE(self);
        auto vector = glm::normalize(self->glm);
        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(

                vector[0],

                vector[1],

                vector[2]

        );
        return result;
    }

    static PyObject *
    FVector3_distance(FVector3 *self, FVector3 *other)
    {
        auto cls = Py_TYPE(self);
        if (Py_TYPE(other) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector3", other);
            return 0;
        }
        auto result = glm::distance(self->glm, other->glm);
        return c_float_to_pyobject(result);
    }




static PyObject *
FVector3_min(FVector3 *self, PyObject *min)
{
    auto c_min = pyobject_to_c_float(min);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::min(self->glm, c_min);
    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector3_max(FVector3 *self, PyObject *max)
{
    auto c_max = pyobject_to_c_float(max);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::max(self->glm, c_max);
    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector3_clamp(FVector3 *self, PyObject *const *args, Py_ssize_t nargs)
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
    FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector3_get_size(FVector3 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 3);
}


static PyObject *
FVector3_get_limits(FVector3 *cls, void *)
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
FVector3_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float) * 3;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (FVector3 *)cls->tp_alloc(cls, 0);
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
FVector3_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->FVector3Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyObject *
FVector3_to_b(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->BVector3_PyTypeObject;
    auto *result = (BVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = BVector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_d(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector3_PyTypeObject;
    auto *result = (DVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_i8(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I8Vector3_PyTypeObject;
    auto *result = (I8Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I8Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_u8(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U8Vector3_PyTypeObject;
    auto *result = (U8Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U8Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_i16(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I16Vector3_PyTypeObject;
    auto *result = (I16Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I16Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_u16(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U16Vector3_PyTypeObject;
    auto *result = (U16Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U16Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_i32(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I32Vector3_PyTypeObject;
    auto *result = (I32Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I32Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_u32(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U32Vector3_PyTypeObject;
    auto *result = (U32Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U32Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_i(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->IVector3_PyTypeObject;
    auto *result = (IVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = IVector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_u(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->UVector3_PyTypeObject;
    auto *result = (UVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = UVector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_i64(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I64Vector3_PyTypeObject;
    auto *result = (I64Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I64Vector3Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector3_to_u64(FVector3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U64Vector3_PyTypeObject;
    auto *result = (U64Vector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U64Vector3Glm(self->glm);
    return (PyObject *)result;
}



static PyMethodDef FVector3_PyMethodDef[] = {


            {"cross", (PyCFunction)FVector3_cross, METH_O, 0},
            {"to_quaternion", (PyCFunction)FVector3_to_quaternion, METH_NOARGS, 0},

        {"lerp", (PyCFunction)FVector3_lerp, METH_FASTCALL, 0},
        {"normalize", (PyCFunction)FVector3_normalize, METH_NOARGS, 0},
        {"distance", (PyCFunction)FVector3_distance, METH_O, 0},

    {"min", (PyCFunction)FVector3_min, METH_O, 0},
    {"max", (PyCFunction)FVector3_max, METH_O, 0},
    {"clamp", (PyCFunction)FVector3_clamp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)FVector3_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)FVector3_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)FVector3_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)FVector3_from_buffer, METH_O | METH_CLASS, 0},

        {"to_b", (PyCFunction)FVector3_to_b, METH_NOARGS, 0},

        {"to_d", (PyCFunction)FVector3_to_d, METH_NOARGS, 0},

        {"to_i8", (PyCFunction)FVector3_to_i8, METH_NOARGS, 0},

        {"to_u8", (PyCFunction)FVector3_to_u8, METH_NOARGS, 0},

        {"to_i16", (PyCFunction)FVector3_to_i16, METH_NOARGS, 0},

        {"to_u16", (PyCFunction)FVector3_to_u16, METH_NOARGS, 0},

        {"to_i32", (PyCFunction)FVector3_to_i32, METH_NOARGS, 0},

        {"to_u32", (PyCFunction)FVector3_to_u32, METH_NOARGS, 0},

        {"to_i", (PyCFunction)FVector3_to_i, METH_NOARGS, 0},

        {"to_u", (PyCFunction)FVector3_to_u, METH_NOARGS, 0},

        {"to_i64", (PyCFunction)FVector3_to_i64, METH_NOARGS, 0},

        {"to_u64", (PyCFunction)FVector3_to_u64, METH_NOARGS, 0},

    {0, 0, 0, 0}
};


static PyType_Slot FVector3_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector3__new__},
    {Py_tp_dealloc, (void*)FVector3__dealloc__},
    {Py_tp_hash, (void*)FVector3__hash__},
    {Py_tp_repr, (void*)FVector3__repr__},
    {Py_sq_length, (void*)FVector3__len__},
    {Py_sq_item, (void*)FVector3__getitem__},
    {Py_tp_richcompare, (void*)FVector3__richcmp__},
    {Py_nb_add, (void*)FVector3__add__},
    {Py_nb_subtract, (void*)FVector3__sub__},
    {Py_nb_multiply, (void*)FVector3__mul__},

        {Py_nb_matrix_multiply, (void*)FVector3__matmul__},
        {Py_nb_remainder, (void*)FVector3__mod__},
        {Py_nb_power, (void*)FVector3__pow__},


        {Py_nb_true_divide, (void*)FVector3__truediv__},


        {Py_nb_negative, (void*)FVector3__neg__},

    {Py_nb_absolute, (void*)FVector3__abs__},
    {Py_nb_bool, (void*)FVector3__bool__},
    {Py_bf_getbuffer, (void*)FVector3_getbufferproc},
    {Py_tp_getset, (void*)FVector3_PyGetSetDef},
    {Py_tp_getattro, (void*)FVector3__getattr__},
    {Py_tp_members, (void*)FVector3_PyMemberDef},
    {Py_tp_methods, (void*)FVector3_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector3_PyTypeSpec = {
    "emath.FVector3",
    sizeof(FVector3),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector3_PyType_Slots
};


static PyTypeObject *
define_FVector3_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector3_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector3", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


    static FVector3 *
    create_FVector3_from_glm(const FVector3Glm& glm)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector3_PyTypeObject;

        FVector3 *result = (FVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(glm);

        return result;
    }



static PyObject *
FVector3Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector3_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector3 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (FVector3Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (FVector3Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new FVector3Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = ((FVector3*)arg)->glm;
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
FVector3Array__dealloc__(FVector3Array *self)
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
FVector3Array__hash__(FVector3Array *self)
{
    Py_ssize_t len = self->length * 3;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (FVector3Glm::length_type j = 0; j < 3; j++)
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
FVector3Array__repr__(FVector3Array *self)
{
    return PyUnicode_FromFormat("FVector3Array[%zu]", self->length);
}


static Py_ssize_t
FVector3Array__len__(FVector3Array *self)
{
    return self->length;
}


static PyObject *
FVector3Array__sq_getitem__(FVector3Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector3_PyTypeObject;

    FVector3 *result = (FVector3 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = FVector3Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
FVector3Array__mp_getitem__(FVector3Array *self, PyObject *key)
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
        auto *result = (FVector3Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new FVector3Glm[length];
            for (FVector3Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->FVector3_PyTypeObject;

        FVector3 *result = (FVector3 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = FVector3Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
FVector3Array__richcmp__(
    FVector3Array *self,
    FVector3Array *other,
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
FVector3Array__bool__(FVector3Array *self)
{
    return self->length ? 1 : 0;
}


static int
FVector3Array_getbufferproc(FVector3Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_BufferError, "FVector3 is read only");
        view->obj = 0;
        return -1;
    }

        if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
        {
            PyErr_SetString(PyExc_BufferError, "FVector3 cannot be made Fortran contiguous");
            view->obj = 0;
            return -1;
        }

    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 3 * self->length;
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
            3
        };
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        static Py_ssize_t strides[] = {
            sizeof(float) * 3,
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
FVector3Array_releasebufferproc(FVector3Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef FVector3Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector3Array, weakreflist), READONLY},
    {0}
};


static PyObject *
FVector3Array_address(FVector3Array *self, void *)
{
    return PyLong_FromVoidPtr(self->glm);
}


static PyObject *
FVector3Array_pointer(FVector3Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FVector3Array_size(FVector3Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 3 * self->length);
}


static PyGetSetDef FVector3Array_PyGetSetDef[] = {
    {"address", (getter)FVector3Array_address, 0, 0, 0},
    {"pointer", (getter)FVector3Array_pointer, 0, 0, 0},
    {"size", (getter)FVector3Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
FVector3Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(float) * 3))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(float), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(float) * 3);

    auto *result = (FVector3Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new FVector3Glm[array_length];
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
FVector3Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->FVector3_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef FVector3Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)FVector3Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)FVector3Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FVector3Array_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector3Array__new__},
    {Py_tp_dealloc, (void*)FVector3Array__dealloc__},
    {Py_tp_hash, (void*)FVector3Array__hash__},
    {Py_tp_repr, (void*)FVector3Array__repr__},
    {Py_sq_length, (void*)FVector3Array__len__},
    {Py_sq_item, (void*)FVector3Array__sq_getitem__},
    {Py_mp_subscript, (void*)FVector3Array__mp_getitem__},
    {Py_tp_richcompare, (void*)FVector3Array__richcmp__},
    {Py_nb_bool, (void*)FVector3Array__bool__},
    {Py_bf_getbuffer, (void*)FVector3Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)FVector3Array_releasebufferproc},
    {Py_tp_getset, (void*)FVector3Array_PyGetSetDef},
    {Py_tp_members, (void*)FVector3Array_PyMemberDef},
    {Py_tp_methods, (void*)FVector3Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector3Array_PyTypeSpec = {
    "emath.FVector3Array",
    sizeof(FVector3Array),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector3Array_PyType_Slots
};


static PyTypeObject *
define_FVector3Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector3Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector3Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_FVector3_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector3_PyTypeObject;
}


static PyTypeObject *
get_FVector3Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector3Array_PyTypeObject;
}


static PyObject *
create_FVector3(const float *value)
{
    auto cls = get_FVector3_type();
    auto result = (FVector3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = *(FVector3Glm *)value;
    return (PyObject *)result;
}


static PyObject *
create_FVector3Array(size_t length, const float *value)
{
    auto cls = get_FVector3Array_type();
    auto result = (FVector3Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new FVector3Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((FVector3Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static const float *
get_FVector3_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector3_type())
    {
        PyErr_Format(PyExc_TypeError, "expected FVector3, got %R", self);
        return 0;
    }
    return (float *)&((FVector3 *)self)->glm;
}


static const float *
get_FVector3Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector3Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector3Array, got %R",
            self
        );
        return 0;
    }
    return (float *)((FVector3Array *)self)->glm;
}


static size_t
get_FVector3Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector3Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector3Array, got %R",
            self
        );
        return 0;
    }
    return ((FVector3Array *)self)->length;
}

#endif

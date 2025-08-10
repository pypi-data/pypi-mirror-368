
// generated from codegen/templates/_vector.hpp

#ifndef E_MATH_FVECTOR4_HPP
#define E_MATH_FVECTOR4_HPP

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
FVector4__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{

        float c_0 = 0;

        float c_1 = 0;

        float c_2 = 0;

        float c_3 = 0;


    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector4 does accept any keyword arguments"
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

                c_3 = arg_c;

            break;
        }

            case 4:
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

                {
                    auto arg = PyTuple_GET_ITEM(args, 3);
                    c_3 = pyobject_to_c_float(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                break;
            }

        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to FVector4, expected "
                "0, 1 or 4 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    FVector4 *self = (FVector4*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = FVector4Glm(

            c_0,

            c_1,

            c_2,

            c_3

    );

    return (PyObject *)self;
}


static void
FVector4__dealloc__(FVector4 *self)
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
FVector4__hash__(FVector4 *self)
{
    Py_ssize_t len = 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (FVector4Glm::length_type i = 0; i < len; i++)
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
FVector4__repr__(FVector4 *self)
{
    PyObject *result = 0;

        PyObject *py_0 = 0;

        PyObject *py_1 = 0;

        PyObject *py_2 = 0;

        PyObject *py_3 = 0;



        py_0 = c_float_to_pyobject(self->glm[0]);
        if (!py_0){ goto cleanup; }

        py_1 = c_float_to_pyobject(self->glm[1]);
        if (!py_1){ goto cleanup; }

        py_2 = c_float_to_pyobject(self->glm[2]);
        if (!py_2){ goto cleanup; }

        py_3 = c_float_to_pyobject(self->glm[3]);
        if (!py_3){ goto cleanup; }

    result = PyUnicode_FromFormat(
        "FVector4("

            "%R, "

            "%R, "

            "%R, "

            "%R"

        ")",

            py_0,

            py_1,

            py_2,

            py_3

    );
cleanup:

        Py_XDECREF(py_0);

        Py_XDECREF(py_1);

        Py_XDECREF(py_2);

        Py_XDECREF(py_3);

    return result;
}


static Py_ssize_t
FVector4__len__(FVector4 *self)
{
    return 4;
}


static PyObject *
FVector4__getitem__(FVector4 *self, Py_ssize_t index)
{
    if (index < 0 || index > 3)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = self->glm[(FVector4Glm::length_type)index];
    return c_float_to_pyobject(c);
}


static PyObject *
FVector4__richcmp__(FVector4 *self, FVector4 *other, int op)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_LT:
        {
            for (FVector4Glm::length_type i = 0; i < 4; i++)
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
            for (FVector4Glm::length_type i = 0; i < 4; i++)
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
            for (FVector4Glm::length_type i = 0; i < 4; i++)
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
            for (FVector4Glm::length_type i = 0; i < 4; i++)
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
FVector4__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector4_PyTypeObject;

    FVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector4 *)left)->glm + ((FVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector4 *)left)->glm + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left + ((FVector4 *)right)->glm;
        }
    }

    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static PyObject *
FVector4__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector4_PyTypeObject;

    FVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector4 *)left)->glm - ((FVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector4 *)left)->glm - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left - ((FVector4 *)right)->glm;
        }
    }

    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static PyObject *
FVector4__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector4_PyTypeObject;

    FVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((FVector4 *)left)->glm * ((FVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((FVector4 *)left)->glm * c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left * ((FVector4 *)right)->glm;
        }
    }

    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}



    static PyObject *
    FVector4__matmul__(FVector4 *left, FVector4 *right)
    {
        auto cls = Py_TYPE(left);
        if (Py_TYPE(left) != Py_TYPE(right)){ Py_RETURN_NOTIMPLEMENTED; }
        auto c_result = glm::dot(left->glm, right->glm);
        return c_float_to_pyobject(c_result);
    }


    static PyObject *
    FVector4__mod__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector4_PyTypeObject;

        FVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::mod(
                ((FVector4 *)left)->glm,
                ((FVector4 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(((FVector4 *)left)->glm, c_right);
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(FVector4Glm(c_left), ((FVector4 *)right)->glm);
            }
        }

        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }


    static PyObject *
    FVector4__pow__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector4_PyTypeObject;

        FVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::pow(
                ((FVector4 *)left)->glm,
                ((FVector4 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(((FVector4 *)left)->glm, FVector4Glm(c_right));
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(FVector4Glm(c_left), ((FVector4 *)right)->glm);
            }
        }

        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }





    static PyObject *
    FVector4__truediv__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector4_PyTypeObject;

        FVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {

            vector = ((FVector4 *)left)->glm / ((FVector4 *)right)->glm;
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_float(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = ((FVector4 *)left)->glm / c_right;
            }
            else
            {
                auto c_left = pyobject_to_c_float(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = c_left / ((FVector4 *)right)->glm;
            }
        }

        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }




    static PyObject *
    FVector4__neg__(FVector4 *self)
    {
        auto cls = Py_TYPE(self);

            FVector4Glm vector = -self->glm;


        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }



static PyObject *
FVector4__abs__(FVector4 *self)
{
    auto cls = Py_TYPE(self);
    FVector4Glm vector = glm::abs(self->glm);

    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static int
FVector4__bool__(FVector4 *self)
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

        if (self->glm[3] == 0)
        {
            return 0;
        }

    return 1;
}


static int
FVector4_getbufferproc(FVector4 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FVector4 is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = &self->glm;
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



    static PyObject *
    FVector4_Getter_0(FVector4 *self, void *)
    {
        auto c = self->glm[0];
        return c_float_to_pyobject(c);
    }

    static PyObject *
    FVector4_Getter_1(FVector4 *self, void *)
    {
        auto c = self->glm[1];
        return c_float_to_pyobject(c);
    }

    static PyObject *
    FVector4_Getter_2(FVector4 *self, void *)
    {
        auto c = self->glm[2];
        return c_float_to_pyobject(c);
    }

    static PyObject *
    FVector4_Getter_3(FVector4 *self, void *)
    {
        auto c = self->glm[3];
        return c_float_to_pyobject(c);
    }




    static PyObject *
    FVector4_magnitude(FVector4 *self, void *)
    {
        auto magnitude = glm::length(self->glm);
        return c_float_to_pyobject(magnitude);
    }



static PyObject *
FVector4_address(FVector4 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)&self->glm);
}


static PyObject *
FVector4_pointer(FVector4 *self, void *)
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


static PyGetSetDef FVector4_PyGetSetDef[] = {
    {"address", (getter)FVector4_address, 0, 0, 0},
    {"x", (getter)FVector4_Getter_0, 0, 0, 0},
    {"r", (getter)FVector4_Getter_0, 0, 0, 0},
    {"s", (getter)FVector4_Getter_0, 0, 0, 0},
    {"u", (getter)FVector4_Getter_0, 0, 0, 0},

        {"y", (getter)FVector4_Getter_1, 0, 0, 0},
        {"g", (getter)FVector4_Getter_1, 0, 0, 0},
        {"t", (getter)FVector4_Getter_1, 0, 0, 0},
        {"v", (getter)FVector4_Getter_1, 0, 0, 0},


        {"z", (getter)FVector4_Getter_2, 0, 0, 0},
        {"b", (getter)FVector4_Getter_2, 0, 0, 0},
        {"p", (getter)FVector4_Getter_2, 0, 0, 0},


        {"w", (getter)FVector4_Getter_3, 0, 0, 0},
        {"a", (getter)FVector4_Getter_3, 0, 0, 0},
        {"q", (getter)FVector4_Getter_3, 0, 0, 0},


        {"magnitude", (getter)FVector4_magnitude, 0, 0, 0},

    {"pointer", (getter)FVector4_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};



    static PyObject *
    swizzle_2_FVector4(FVector4 *self, PyObject *py_attr)
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


                    case 'w':
                    case 'a':
                    case 'q':
                        glm_index = 3;
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
    swizzle_3_FVector4(FVector4 *self, PyObject *py_attr)
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


                    case 'w':
                    case 'a':
                    case 'q':
                        glm_index = 3;
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
    swizzle_4_FVector4(FVector4 *self, PyObject *py_attr)
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


                    case 'w':
                    case 'a':
                    case 'q':
                        glm_index = 3;
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
FVector4__getattr__(FVector4 *self, PyObject *py_attr)
{
    PyObject *result = PyObject_GenericGetAttr((PyObject *)self, py_attr);
    if (result != 0){ return result; }

    auto attr_length = PyUnicode_GET_LENGTH(py_attr);
    switch(attr_length)
    {
        case 2:
        {
            PyErr_Clear();
            return swizzle_2_FVector4(self, py_attr);
        }
        case 3:
        {
            PyErr_Clear();
            return swizzle_3_FVector4(self, py_attr);
        }
        case 4:
        {
            PyErr_Clear();
            return swizzle_4_FVector4(self, py_attr);
        }
    }
    return 0;
}


static PyMemberDef FVector4_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector4, weakreflist), READONLY},
    {0}
};






    static PyObject *
    FVector4_lerp(FVector4 *self, PyObject *const *args, Py_ssize_t nargs)
    {
        if (nargs != 2)
        {
            PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
            return 0;
        }

        auto cls = Py_TYPE(self);
        if (Py_TYPE(args[0]) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector4", args[0]);
            return 0;
        }
        auto other = (FVector4 *)args[0];

        auto c_x = pyobject_to_c_float(args[1]);
        if (PyErr_Occurred()){ return 0; }


            auto vector = glm::lerp(self->glm, other->glm, c_x);

        auto result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(vector);
        return (PyObject *)result;
    }


    static FVector4 *
    FVector4_normalize(FVector4 *self, void*)
    {
        auto cls = Py_TYPE(self);
        auto vector = glm::normalize(self->glm);
        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );
        return result;
    }

    static PyObject *
    FVector4_distance(FVector4 *self, FVector4 *other)
    {
        auto cls = Py_TYPE(self);
        if (Py_TYPE(other) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not FVector4", other);
            return 0;
        }
        auto result = glm::distance(self->glm, other->glm);
        return c_float_to_pyobject(result);
    }




static PyObject *
FVector4_min(FVector4 *self, PyObject *min)
{
    auto c_min = pyobject_to_c_float(min);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::min(self->glm, c_min);
    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector4_max(FVector4 *self, PyObject *max)
{
    auto c_max = pyobject_to_c_float(max);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::max(self->glm, c_max);
    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector4_clamp(FVector4 *self, PyObject *const *args, Py_ssize_t nargs)
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
    FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
FVector4_get_size(FVector4 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 4);
}


static PyObject *
FVector4_get_limits(FVector4 *cls, void *)
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
FVector4_from_buffer(PyTypeObject *cls, PyObject *buffer)
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

    auto *result = (FVector4 *)cls->tp_alloc(cls, 0);
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
FVector4_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->FVector4Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyObject *
FVector4_to_b(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->BVector4_PyTypeObject;
    auto *result = (BVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = BVector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_d(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector4_PyTypeObject;
    auto *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_i8(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I8Vector4_PyTypeObject;
    auto *result = (I8Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I8Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_u8(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U8Vector4_PyTypeObject;
    auto *result = (U8Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U8Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_i16(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I16Vector4_PyTypeObject;
    auto *result = (I16Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I16Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_u16(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U16Vector4_PyTypeObject;
    auto *result = (U16Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U16Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_i32(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I32Vector4_PyTypeObject;
    auto *result = (I32Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I32Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_u32(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U32Vector4_PyTypeObject;
    auto *result = (U32Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U32Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_i(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->IVector4_PyTypeObject;
    auto *result = (IVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = IVector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_u(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->UVector4_PyTypeObject;
    auto *result = (UVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = UVector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_i64(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->I64Vector4_PyTypeObject;
    auto *result = (I64Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = I64Vector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
FVector4_to_u64(FVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U64Vector4_PyTypeObject;
    auto *result = (U64Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U64Vector4Glm(self->glm);
    return (PyObject *)result;
}



static PyMethodDef FVector4_PyMethodDef[] = {


        {"lerp", (PyCFunction)FVector4_lerp, METH_FASTCALL, 0},
        {"normalize", (PyCFunction)FVector4_normalize, METH_NOARGS, 0},
        {"distance", (PyCFunction)FVector4_distance, METH_O, 0},

    {"min", (PyCFunction)FVector4_min, METH_O, 0},
    {"max", (PyCFunction)FVector4_max, METH_O, 0},
    {"clamp", (PyCFunction)FVector4_clamp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)FVector4_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)FVector4_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)FVector4_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)FVector4_from_buffer, METH_O | METH_CLASS, 0},

        {"to_b", (PyCFunction)FVector4_to_b, METH_NOARGS, 0},

        {"to_d", (PyCFunction)FVector4_to_d, METH_NOARGS, 0},

        {"to_i8", (PyCFunction)FVector4_to_i8, METH_NOARGS, 0},

        {"to_u8", (PyCFunction)FVector4_to_u8, METH_NOARGS, 0},

        {"to_i16", (PyCFunction)FVector4_to_i16, METH_NOARGS, 0},

        {"to_u16", (PyCFunction)FVector4_to_u16, METH_NOARGS, 0},

        {"to_i32", (PyCFunction)FVector4_to_i32, METH_NOARGS, 0},

        {"to_u32", (PyCFunction)FVector4_to_u32, METH_NOARGS, 0},

        {"to_i", (PyCFunction)FVector4_to_i, METH_NOARGS, 0},

        {"to_u", (PyCFunction)FVector4_to_u, METH_NOARGS, 0},

        {"to_i64", (PyCFunction)FVector4_to_i64, METH_NOARGS, 0},

        {"to_u64", (PyCFunction)FVector4_to_u64, METH_NOARGS, 0},

    {0, 0, 0, 0}
};


static PyType_Slot FVector4_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector4__new__},
    {Py_tp_dealloc, (void*)FVector4__dealloc__},
    {Py_tp_hash, (void*)FVector4__hash__},
    {Py_tp_repr, (void*)FVector4__repr__},
    {Py_sq_length, (void*)FVector4__len__},
    {Py_sq_item, (void*)FVector4__getitem__},
    {Py_tp_richcompare, (void*)FVector4__richcmp__},
    {Py_nb_add, (void*)FVector4__add__},
    {Py_nb_subtract, (void*)FVector4__sub__},
    {Py_nb_multiply, (void*)FVector4__mul__},

        {Py_nb_matrix_multiply, (void*)FVector4__matmul__},
        {Py_nb_remainder, (void*)FVector4__mod__},
        {Py_nb_power, (void*)FVector4__pow__},


        {Py_nb_true_divide, (void*)FVector4__truediv__},


        {Py_nb_negative, (void*)FVector4__neg__},

    {Py_nb_absolute, (void*)FVector4__abs__},
    {Py_nb_bool, (void*)FVector4__bool__},
    {Py_bf_getbuffer, (void*)FVector4_getbufferproc},
    {Py_tp_getset, (void*)FVector4_PyGetSetDef},
    {Py_tp_getattro, (void*)FVector4__getattr__},
    {Py_tp_members, (void*)FVector4_PyMemberDef},
    {Py_tp_methods, (void*)FVector4_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector4_PyTypeSpec = {
    "emath.FVector4",
    sizeof(FVector4),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector4_PyType_Slots
};


static PyTypeObject *
define_FVector4_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector4_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector4", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


    static FVector4 *
    create_FVector4_from_glm(const FVector4Glm& glm)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FVector4_PyTypeObject;

        FVector4 *result = (FVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(glm);

        return result;
    }



static PyObject *
FVector4Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector4_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FVector4 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (FVector4Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (FVector4Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new FVector4Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = ((FVector4*)arg)->glm;
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
FVector4Array__dealloc__(FVector4Array *self)
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
FVector4Array__hash__(FVector4Array *self)
{
    Py_ssize_t len = self->length * 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (FVector4Glm::length_type j = 0; j < 4; j++)
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
FVector4Array__repr__(FVector4Array *self)
{
    return PyUnicode_FromFormat("FVector4Array[%zu]", self->length);
}


static Py_ssize_t
FVector4Array__len__(FVector4Array *self)
{
    return self->length;
}


static PyObject *
FVector4Array__sq_getitem__(FVector4Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FVector4_PyTypeObject;

    FVector4 *result = (FVector4 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
FVector4Array__mp_getitem__(FVector4Array *self, PyObject *key)
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
        auto *result = (FVector4Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new FVector4Glm[length];
            for (FVector4Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->FVector4_PyTypeObject;

        FVector4 *result = (FVector4 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = FVector4Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
FVector4Array__richcmp__(
    FVector4Array *self,
    FVector4Array *other,
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
FVector4Array__bool__(FVector4Array *self)
{
    return self->length ? 1 : 0;
}


static int
FVector4Array_getbufferproc(FVector4Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_BufferError, "FVector4 is read only");
        view->obj = 0;
        return -1;
    }

        if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
        {
            PyErr_SetString(PyExc_BufferError, "FVector4 cannot be made Fortran contiguous");
            view->obj = 0;
            return -1;
        }

    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 4 * self->length;
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
FVector4Array_releasebufferproc(FVector4Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef FVector4Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FVector4Array, weakreflist), READONLY},
    {0}
};


static PyObject *
FVector4Array_address(FVector4Array *self, void *)
{
    return PyLong_FromVoidPtr(self->glm);
}


static PyObject *
FVector4Array_pointer(FVector4Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FVector4Array_size(FVector4Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 4 * self->length);
}


static PyGetSetDef FVector4Array_PyGetSetDef[] = {
    {"address", (getter)FVector4Array_address, 0, 0, 0},
    {"pointer", (getter)FVector4Array_pointer, 0, 0, 0},
    {"size", (getter)FVector4Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
FVector4Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
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

    auto *result = (FVector4Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new FVector4Glm[array_length];
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
FVector4Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->FVector4_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef FVector4Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)FVector4Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)FVector4Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FVector4Array_PyType_Slots [] = {
    {Py_tp_new, (void*)FVector4Array__new__},
    {Py_tp_dealloc, (void*)FVector4Array__dealloc__},
    {Py_tp_hash, (void*)FVector4Array__hash__},
    {Py_tp_repr, (void*)FVector4Array__repr__},
    {Py_sq_length, (void*)FVector4Array__len__},
    {Py_sq_item, (void*)FVector4Array__sq_getitem__},
    {Py_mp_subscript, (void*)FVector4Array__mp_getitem__},
    {Py_tp_richcompare, (void*)FVector4Array__richcmp__},
    {Py_nb_bool, (void*)FVector4Array__bool__},
    {Py_bf_getbuffer, (void*)FVector4Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)FVector4Array_releasebufferproc},
    {Py_tp_getset, (void*)FVector4Array_PyGetSetDef},
    {Py_tp_members, (void*)FVector4Array_PyMemberDef},
    {Py_tp_methods, (void*)FVector4Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec FVector4Array_PyTypeSpec = {
    "emath.FVector4Array",
    sizeof(FVector4Array),
    0,
    Py_TPFLAGS_DEFAULT,
    FVector4Array_PyType_Slots
};


static PyTypeObject *
define_FVector4Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FVector4Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FVector4Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_FVector4_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector4_PyTypeObject;
}


static PyTypeObject *
get_FVector4Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FVector4Array_PyTypeObject;
}


static PyObject *
create_FVector4(const float *value)
{
    auto cls = get_FVector4_type();
    auto result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = *(FVector4Glm *)value;
    return (PyObject *)result;
}


static PyObject *
create_FVector4Array(size_t length, const float *value)
{
    auto cls = get_FVector4Array_type();
    auto result = (FVector4Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new FVector4Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((FVector4Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static const float *
get_FVector4_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector4_type())
    {
        PyErr_Format(PyExc_TypeError, "expected FVector4, got %R", self);
        return 0;
    }
    return (float *)&((FVector4 *)self)->glm;
}


static const float *
get_FVector4Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector4Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector4Array, got %R",
            self
        );
        return 0;
    }
    return (float *)((FVector4Array *)self)->glm;
}


static size_t
get_FVector4Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_FVector4Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FVector4Array, got %R",
            self
        );
        return 0;
    }
    return ((FVector4Array *)self)->length;
}

#endif


// generated from codegen/templates/_vector.hpp

#ifndef E_MATH_DVECTOR4_HPP
#define E_MATH_DVECTOR4_HPP

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
DVector4__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{

        double c_0 = 0;

        double c_1 = 0;

        double c_2 = 0;

        double c_3 = 0;


    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DVector4 does accept any keyword arguments"
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
            double arg_c = pyobject_to_c_double(arg);
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
                    c_0 = pyobject_to_c_double(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                {
                    auto arg = PyTuple_GET_ITEM(args, 1);
                    c_1 = pyobject_to_c_double(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                {
                    auto arg = PyTuple_GET_ITEM(args, 2);
                    c_2 = pyobject_to_c_double(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                {
                    auto arg = PyTuple_GET_ITEM(args, 3);
                    c_3 = pyobject_to_c_double(arg);
                    auto error_occurred = PyErr_Occurred();
                    if (error_occurred){ return 0; }
                }

                break;
            }

        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to DVector4, expected "
                "0, 1 or 4 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    DVector4 *self = (DVector4*)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->glm = DVector4Glm(

            c_0,

            c_1,

            c_2,

            c_3

    );

    return (PyObject *)self;
}


static void
DVector4__dealloc__(DVector4 *self)
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
DVector4__hash__(DVector4 *self)
{
    Py_ssize_t len = 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (DVector4Glm::length_type i = 0; i < len; i++)
    {
        Py_uhash_t lane = std::hash<double>{}(self->glm[i]);
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
DVector4__repr__(DVector4 *self)
{
    PyObject *result = 0;

        PyObject *py_0 = 0;

        PyObject *py_1 = 0;

        PyObject *py_2 = 0;

        PyObject *py_3 = 0;



        py_0 = c_double_to_pyobject(self->glm[0]);
        if (!py_0){ goto cleanup; }

        py_1 = c_double_to_pyobject(self->glm[1]);
        if (!py_1){ goto cleanup; }

        py_2 = c_double_to_pyobject(self->glm[2]);
        if (!py_2){ goto cleanup; }

        py_3 = c_double_to_pyobject(self->glm[3]);
        if (!py_3){ goto cleanup; }

    result = PyUnicode_FromFormat(
        "DVector4("

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
DVector4__len__(DVector4 *self)
{
    return 4;
}


static PyObject *
DVector4__getitem__(DVector4 *self, Py_ssize_t index)
{
    if (index < 0 || index > 3)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    auto c = self->glm[(DVector4Glm::length_type)index];
    return c_double_to_pyobject(c);
}


static PyObject *
DVector4__richcmp__(DVector4 *self, DVector4 *other, int op)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_LT:
        {
            for (DVector4Glm::length_type i = 0; i < 4; i++)
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
            for (DVector4Glm::length_type i = 0; i < 4; i++)
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
            for (DVector4Glm::length_type i = 0; i < 4; i++)
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
            for (DVector4Glm::length_type i = 0; i < 4; i++)
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
DVector4__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector4_PyTypeObject;

    DVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((DVector4 *)left)->glm + ((DVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((DVector4 *)left)->glm + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_double(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left + ((DVector4 *)right)->glm;
        }
    }

    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static PyObject *
DVector4__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector4_PyTypeObject;

    DVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((DVector4 *)left)->glm - ((DVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((DVector4 *)left)->glm - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_double(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left - ((DVector4 *)right)->glm;
        }
    }

    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static PyObject *
DVector4__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DVector4_PyTypeObject;

    DVector4Glm vector;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        vector = ((DVector4 *)left)->glm * ((DVector4 *)right)->glm;
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = ((DVector4 *)left)->glm * c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_double(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            vector = c_left * ((DVector4 *)right)->glm;
        }
    }

    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}



    static PyObject *
    DVector4__matmul__(DVector4 *left, DVector4 *right)
    {
        auto cls = Py_TYPE(left);
        if (Py_TYPE(left) != Py_TYPE(right)){ Py_RETURN_NOTIMPLEMENTED; }
        auto c_result = glm::dot(left->glm, right->glm);
        return c_double_to_pyobject(c_result);
    }


    static PyObject *
    DVector4__mod__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->DVector4_PyTypeObject;

        DVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::mod(
                ((DVector4 *)left)->glm,
                ((DVector4 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_double(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(((DVector4 *)left)->glm, c_right);
            }
            else
            {
                auto c_left = pyobject_to_c_double(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::mod(DVector4Glm(c_left), ((DVector4 *)right)->glm);
            }
        }

        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }


    static PyObject *
    DVector4__pow__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->DVector4_PyTypeObject;

        DVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {
            vector = glm::pow(
                ((DVector4 *)left)->glm,
                ((DVector4 *)right)->glm
            );
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_double(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(((DVector4 *)left)->glm, DVector4Glm(c_right));
            }
            else
            {
                auto c_left = pyobject_to_c_double(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
                vector = glm::pow(DVector4Glm(c_left), ((DVector4 *)right)->glm);
            }
        }

        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }





    static PyObject *
    DVector4__truediv__(PyObject *left, PyObject *right)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->DVector4_PyTypeObject;

        DVector4Glm vector;
        if (Py_TYPE(left) == Py_TYPE(right))
        {

            vector = ((DVector4 *)left)->glm / ((DVector4 *)right)->glm;
        }
        else
        {
            if (Py_TYPE(left) == cls)
            {
                auto c_right = pyobject_to_c_double(right);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = ((DVector4 *)left)->glm / c_right;
            }
            else
            {
                auto c_left = pyobject_to_c_double(left);
                if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                vector = c_left / ((DVector4 *)right)->glm;
            }
        }

        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }




    static PyObject *
    DVector4__neg__(DVector4 *self)
    {
        auto cls = Py_TYPE(self);

            DVector4Glm vector = -self->glm;


        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );

        return (PyObject *)result;
    }



static PyObject *
DVector4__abs__(DVector4 *self)
{
    auto cls = Py_TYPE(self);
    DVector4Glm vector = glm::abs(self->glm);

    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(

            vector[0],

            vector[1],

            vector[2],

            vector[3]

    );

    return (PyObject *)result;
}


static int
DVector4__bool__(DVector4 *self)
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
DVector4_getbufferproc(DVector4 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "DVector4 is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = &self->glm;
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



    static PyObject *
    DVector4_Getter_0(DVector4 *self, void *)
    {
        auto c = self->glm[0];
        return c_double_to_pyobject(c);
    }

    static PyObject *
    DVector4_Getter_1(DVector4 *self, void *)
    {
        auto c = self->glm[1];
        return c_double_to_pyobject(c);
    }

    static PyObject *
    DVector4_Getter_2(DVector4 *self, void *)
    {
        auto c = self->glm[2];
        return c_double_to_pyobject(c);
    }

    static PyObject *
    DVector4_Getter_3(DVector4 *self, void *)
    {
        auto c = self->glm[3];
        return c_double_to_pyobject(c);
    }




    static PyObject *
    DVector4_magnitude(DVector4 *self, void *)
    {
        auto magnitude = glm::length(self->glm);
        return c_double_to_pyobject(magnitude);
    }



static PyObject *
DVector4_address(DVector4 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)&self->glm);
}


static PyObject *
DVector4_pointer(DVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }

    auto void_p_cls = module_state->ctypes_c_void_p;
    auto void_p = PyObject_CallFunction(void_p_cls, "n", (Py_ssize_t)&self->glm);
    if (!void_p){ return 0; }

    auto c_p = module_state->ctypes_c_double_p;
    auto result = PyObject_CallFunction(module_state->ctypes_cast, "OO", void_p, c_p);
    Py_DECREF(void_p);
    return result;
}


static PyGetSetDef DVector4_PyGetSetDef[] = {
    {"address", (getter)DVector4_address, 0, 0, 0},
    {"x", (getter)DVector4_Getter_0, 0, 0, 0},
    {"r", (getter)DVector4_Getter_0, 0, 0, 0},
    {"s", (getter)DVector4_Getter_0, 0, 0, 0},
    {"u", (getter)DVector4_Getter_0, 0, 0, 0},

        {"y", (getter)DVector4_Getter_1, 0, 0, 0},
        {"g", (getter)DVector4_Getter_1, 0, 0, 0},
        {"t", (getter)DVector4_Getter_1, 0, 0, 0},
        {"v", (getter)DVector4_Getter_1, 0, 0, 0},


        {"z", (getter)DVector4_Getter_2, 0, 0, 0},
        {"b", (getter)DVector4_Getter_2, 0, 0, 0},
        {"p", (getter)DVector4_Getter_2, 0, 0, 0},


        {"w", (getter)DVector4_Getter_3, 0, 0, 0},
        {"a", (getter)DVector4_Getter_3, 0, 0, 0},
        {"q", (getter)DVector4_Getter_3, 0, 0, 0},


        {"magnitude", (getter)DVector4_magnitude, 0, 0, 0},

    {"pointer", (getter)DVector4_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};



    static PyObject *
    swizzle_2_DVector4(DVector4 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        DVector2Glm vec;
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
        auto cls = module_state->DVector2_PyTypeObject;

        DVector2 *result = (DVector2 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector2Glm(vec);

        return (PyObject *)result;
    }



    static PyObject *
    swizzle_3_DVector4(DVector4 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        DVector3Glm vec;
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
        auto cls = module_state->DVector3_PyTypeObject;

        DVector3 *result = (DVector3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector3Glm(vec);

        return (PyObject *)result;
    }



    static PyObject *
    swizzle_4_DVector4(DVector4 *self, PyObject *py_attr)
    {
        const char *attr = PyUnicode_AsUTF8(py_attr);
        if (!attr){ return 0; }

        DVector4Glm vec;
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
        auto cls = module_state->DVector4_PyTypeObject;

        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(vec);

        return (PyObject *)result;
    }




static PyObject *
DVector4__getattr__(DVector4 *self, PyObject *py_attr)
{
    PyObject *result = PyObject_GenericGetAttr((PyObject *)self, py_attr);
    if (result != 0){ return result; }

    auto attr_length = PyUnicode_GET_LENGTH(py_attr);
    switch(attr_length)
    {
        case 2:
        {
            PyErr_Clear();
            return swizzle_2_DVector4(self, py_attr);
        }
        case 3:
        {
            PyErr_Clear();
            return swizzle_3_DVector4(self, py_attr);
        }
        case 4:
        {
            PyErr_Clear();
            return swizzle_4_DVector4(self, py_attr);
        }
    }
    return 0;
}


static PyMemberDef DVector4_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DVector4, weakreflist), READONLY},
    {0}
};






    static PyObject *
    DVector4_lerp(DVector4 *self, PyObject *const *args, Py_ssize_t nargs)
    {
        if (nargs != 2)
        {
            PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
            return 0;
        }

        auto cls = Py_TYPE(self);
        if (Py_TYPE(args[0]) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not DVector4", args[0]);
            return 0;
        }
        auto other = (DVector4 *)args[0];

        auto c_x = pyobject_to_c_double(args[1]);
        if (PyErr_Occurred()){ return 0; }


            auto vector = glm::lerp(self->glm, other->glm, c_x);

        auto result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(vector);
        return (PyObject *)result;
    }


    static DVector4 *
    DVector4_normalize(DVector4 *self, void*)
    {
        auto cls = Py_TYPE(self);
        auto vector = glm::normalize(self->glm);
        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(

                vector[0],

                vector[1],

                vector[2],

                vector[3]

        );
        return result;
    }

    static PyObject *
    DVector4_distance(DVector4 *self, DVector4 *other)
    {
        auto cls = Py_TYPE(self);
        if (Py_TYPE(other) != cls)
        {
            PyErr_Format(PyExc_TypeError, "%R is not DVector4", other);
            return 0;
        }
        auto result = glm::distance(self->glm, other->glm);
        return c_double_to_pyobject(result);
    }




static PyObject *
DVector4_min(DVector4 *self, PyObject *min)
{
    auto c_min = pyobject_to_c_double(min);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::min(self->glm, c_min);
    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
DVector4_max(DVector4 *self, PyObject *max)
{
    auto c_max = pyobject_to_c_double(max);
    if (PyErr_Occurred()){ return 0; }
    auto cls = Py_TYPE(self);
    auto vector = glm::max(self->glm, c_max);
    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
DVector4_clamp(DVector4 *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 2)
    {
        PyErr_Format(PyExc_TypeError, "expected 2 arguments, got %zi", nargs);
        return 0;
    }
    auto c_min = pyobject_to_c_double(args[0]);
    if (PyErr_Occurred()){ return 0; }
    auto c_max = pyobject_to_c_double(args[1]);
    if (PyErr_Occurred()){ return 0; }

    auto cls = Py_TYPE(self);
    auto vector = glm::clamp(self->glm, c_min, c_max);
    DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(vector);
    return (PyObject *)result;
}


static PyObject *
DVector4_get_size(DVector4 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 4);
}


static PyObject *
DVector4_get_limits(DVector4 *cls, void *)
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
DVector4_from_buffer(PyTypeObject *cls, PyObject *buffer)
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

    auto *result = (DVector4 *)cls->tp_alloc(cls, 0);
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
DVector4_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->DVector4Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyObject *
DVector4_to_b(DVector4 *self, void *)
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
DVector4_to_f(DVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FVector4_PyTypeObject;
    auto *result = (FVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = FVector4Glm(self->glm);
    return (PyObject *)result;
}

static PyObject *
DVector4_to_i8(DVector4 *self, void *)
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
DVector4_to_u8(DVector4 *self, void *)
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
DVector4_to_i16(DVector4 *self, void *)
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
DVector4_to_u16(DVector4 *self, void *)
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
DVector4_to_i32(DVector4 *self, void *)
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
DVector4_to_u32(DVector4 *self, void *)
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
DVector4_to_i(DVector4 *self, void *)
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
DVector4_to_u(DVector4 *self, void *)
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
DVector4_to_i64(DVector4 *self, void *)
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
DVector4_to_u64(DVector4 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->U64Vector4_PyTypeObject;
    auto *result = (U64Vector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = U64Vector4Glm(self->glm);
    return (PyObject *)result;
}



static PyMethodDef DVector4_PyMethodDef[] = {


        {"lerp", (PyCFunction)DVector4_lerp, METH_FASTCALL, 0},
        {"normalize", (PyCFunction)DVector4_normalize, METH_NOARGS, 0},
        {"distance", (PyCFunction)DVector4_distance, METH_O, 0},

    {"min", (PyCFunction)DVector4_min, METH_O, 0},
    {"max", (PyCFunction)DVector4_max, METH_O, 0},
    {"clamp", (PyCFunction)DVector4_clamp, METH_FASTCALL, 0},
    {"get_limits", (PyCFunction)DVector4_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)DVector4_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)DVector4_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)DVector4_from_buffer, METH_O | METH_CLASS, 0},

        {"to_b", (PyCFunction)DVector4_to_b, METH_NOARGS, 0},

        {"to_f", (PyCFunction)DVector4_to_f, METH_NOARGS, 0},

        {"to_i8", (PyCFunction)DVector4_to_i8, METH_NOARGS, 0},

        {"to_u8", (PyCFunction)DVector4_to_u8, METH_NOARGS, 0},

        {"to_i16", (PyCFunction)DVector4_to_i16, METH_NOARGS, 0},

        {"to_u16", (PyCFunction)DVector4_to_u16, METH_NOARGS, 0},

        {"to_i32", (PyCFunction)DVector4_to_i32, METH_NOARGS, 0},

        {"to_u32", (PyCFunction)DVector4_to_u32, METH_NOARGS, 0},

        {"to_i", (PyCFunction)DVector4_to_i, METH_NOARGS, 0},

        {"to_u", (PyCFunction)DVector4_to_u, METH_NOARGS, 0},

        {"to_i64", (PyCFunction)DVector4_to_i64, METH_NOARGS, 0},

        {"to_u64", (PyCFunction)DVector4_to_u64, METH_NOARGS, 0},

    {0, 0, 0, 0}
};


static PyType_Slot DVector4_PyType_Slots [] = {
    {Py_tp_new, (void*)DVector4__new__},
    {Py_tp_dealloc, (void*)DVector4__dealloc__},
    {Py_tp_hash, (void*)DVector4__hash__},
    {Py_tp_repr, (void*)DVector4__repr__},
    {Py_sq_length, (void*)DVector4__len__},
    {Py_sq_item, (void*)DVector4__getitem__},
    {Py_tp_richcompare, (void*)DVector4__richcmp__},
    {Py_nb_add, (void*)DVector4__add__},
    {Py_nb_subtract, (void*)DVector4__sub__},
    {Py_nb_multiply, (void*)DVector4__mul__},

        {Py_nb_matrix_multiply, (void*)DVector4__matmul__},
        {Py_nb_remainder, (void*)DVector4__mod__},
        {Py_nb_power, (void*)DVector4__pow__},


        {Py_nb_true_divide, (void*)DVector4__truediv__},


        {Py_nb_negative, (void*)DVector4__neg__},

    {Py_nb_absolute, (void*)DVector4__abs__},
    {Py_nb_bool, (void*)DVector4__bool__},
    {Py_bf_getbuffer, (void*)DVector4_getbufferproc},
    {Py_tp_getset, (void*)DVector4_PyGetSetDef},
    {Py_tp_getattro, (void*)DVector4__getattr__},
    {Py_tp_members, (void*)DVector4_PyMemberDef},
    {Py_tp_methods, (void*)DVector4_PyMethodDef},
    {0, 0},
};


static PyType_Spec DVector4_PyTypeSpec = {
    "emath.DVector4",
    sizeof(DVector4),
    0,
    Py_TPFLAGS_DEFAULT,
    DVector4_PyType_Slots
};


static PyTypeObject *
define_DVector4_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DVector4_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DVector4", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


    static DVector4 *
    create_DVector4_from_glm(const DVector4Glm& glm)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->DVector4_PyTypeObject;

        DVector4 *result = (DVector4 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(glm);

        return result;
    }



static PyObject *
DVector4Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DVector4_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DVector4 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (DVector4Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (DVector4Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new DVector4Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = ((DVector4*)arg)->glm;
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
DVector4Array__dealloc__(DVector4Array *self)
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
DVector4Array__hash__(DVector4Array *self)
{
    Py_ssize_t len = self->length * 4;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (DVector4Glm::length_type j = 0; j < 4; j++)
        {
            Py_uhash_t lane = std::hash<double>{}(self->glm[i][j]);
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
DVector4Array__repr__(DVector4Array *self)
{
    return PyUnicode_FromFormat("DVector4Array[%zu]", self->length);
}


static Py_ssize_t
DVector4Array__len__(DVector4Array *self)
{
    return self->length;
}


static PyObject *
DVector4Array__sq_getitem__(DVector4Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DVector4_PyTypeObject;

    DVector4 *result = (DVector4 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = DVector4Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
DVector4Array__mp_getitem__(DVector4Array *self, PyObject *key)
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
        auto *result = (DVector4Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new DVector4Glm[length];
            for (DVector4Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->DVector4_PyTypeObject;

        DVector4 *result = (DVector4 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = DVector4Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
DVector4Array__richcmp__(
    DVector4Array *self,
    DVector4Array *other,
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
DVector4Array__bool__(DVector4Array *self)
{
    return self->length ? 1 : 0;
}


static int
DVector4Array_getbufferproc(DVector4Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_BufferError, "DVector4 is read only");
        view->obj = 0;
        return -1;
    }

        if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
        {
            PyErr_SetString(PyExc_BufferError, "DVector4 cannot be made Fortran contiguous");
            view->obj = 0;
            return -1;
        }

    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(double) * 4 * self->length;
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
DVector4Array_releasebufferproc(DVector4Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef DVector4Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DVector4Array, weakreflist), READONLY},
    {0}
};


static PyObject *
DVector4Array_address(DVector4Array *self, void *)
{
    return PyLong_FromVoidPtr(self->glm);
}


static PyObject *
DVector4Array_pointer(DVector4Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_double_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
DVector4Array_size(DVector4Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 4 * self->length);
}


static PyGetSetDef DVector4Array_PyGetSetDef[] = {
    {"address", (getter)DVector4Array_address, 0, 0, 0},
    {"pointer", (getter)DVector4Array_pointer, 0, 0, 0},
    {"size", (getter)DVector4Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
DVector4Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
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

    auto *result = (DVector4Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new DVector4Glm[array_length];
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
DVector4Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->DVector4_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef DVector4Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)DVector4Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)DVector4Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot DVector4Array_PyType_Slots [] = {
    {Py_tp_new, (void*)DVector4Array__new__},
    {Py_tp_dealloc, (void*)DVector4Array__dealloc__},
    {Py_tp_hash, (void*)DVector4Array__hash__},
    {Py_tp_repr, (void*)DVector4Array__repr__},
    {Py_sq_length, (void*)DVector4Array__len__},
    {Py_sq_item, (void*)DVector4Array__sq_getitem__},
    {Py_mp_subscript, (void*)DVector4Array__mp_getitem__},
    {Py_tp_richcompare, (void*)DVector4Array__richcmp__},
    {Py_nb_bool, (void*)DVector4Array__bool__},
    {Py_bf_getbuffer, (void*)DVector4Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)DVector4Array_releasebufferproc},
    {Py_tp_getset, (void*)DVector4Array_PyGetSetDef},
    {Py_tp_members, (void*)DVector4Array_PyMemberDef},
    {Py_tp_methods, (void*)DVector4Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec DVector4Array_PyTypeSpec = {
    "emath.DVector4Array",
    sizeof(DVector4Array),
    0,
    Py_TPFLAGS_DEFAULT,
    DVector4Array_PyType_Slots
};


static PyTypeObject *
define_DVector4Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DVector4Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DVector4Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_DVector4_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DVector4_PyTypeObject;
}


static PyTypeObject *
get_DVector4Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DVector4Array_PyTypeObject;
}


static PyObject *
create_DVector4(const double *value)
{
    auto cls = get_DVector4_type();
    auto result = (DVector4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = *(DVector4Glm *)value;
    return (PyObject *)result;
}


static PyObject *
create_DVector4Array(size_t length, const double *value)
{
    auto cls = get_DVector4Array_type();
    auto result = (DVector4Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new DVector4Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((DVector4Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static const double *
get_DVector4_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DVector4_type())
    {
        PyErr_Format(PyExc_TypeError, "expected DVector4, got %R", self);
        return 0;
    }
    return (double *)&((DVector4 *)self)->glm;
}


static const double *
get_DVector4Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DVector4Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DVector4Array, got %R",
            self
        );
        return 0;
    }
    return (double *)((DVector4Array *)self)->glm;
}


static size_t
get_DVector4Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_DVector4Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DVector4Array, got %R",
            self
        );
        return 0;
    }
    return ((DVector4Array *)self)->length;
}

#endif

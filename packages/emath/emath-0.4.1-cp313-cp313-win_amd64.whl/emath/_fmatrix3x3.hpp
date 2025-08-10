
// generated from codegen/templates/_matrix.hpp

#ifndef E_MATH_FMATRIX3X3_HPP
#define E_MATH_FMATRIX3X3_HPP

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
#include "_vectortype.hpp"
#include "_matrixtype.hpp"
#include "_type.hpp"


static PyObject *
FMatrix3x3__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FMatrix3x3 does accept any keyword arguments"
        );
        return 0;
    }

    FMatrix3x3Glm *glm = 0;
    auto arg_count = PyTuple_GET_SIZE(args);
    switch (PyTuple_GET_SIZE(args))
    {
        case 0:
        {
            glm = new FMatrix3x3Glm();
            break;
        }
        case 1:
        {
            auto arg = PyTuple_GET_ITEM(args, 0);
            float arg_c = pyobject_to_c_float(arg);
            auto error_occurred = PyErr_Occurred();
            if (error_occurred){ return 0; }
            glm = new FMatrix3x3Glm(arg_c);
            break;
        }
        case 3:
        {
            auto module_state = get_module_state();
            if (!module_state){ return 0; }
            auto column_cls = module_state->FVector3_PyTypeObject;

                PyObject *p_0 = PyTuple_GET_ITEM(args, 0);
                if (Py_TYPE(p_0) != column_cls)
                {
                    PyErr_Format(
                        PyExc_TypeError,
                        "invalid column supplied, expected %R, (got %R)",
                        column_cls,
                        p_0
                    );
                    return 0;
                }

                PyObject *p_1 = PyTuple_GET_ITEM(args, 1);
                if (Py_TYPE(p_1) != column_cls)
                {
                    PyErr_Format(
                        PyExc_TypeError,
                        "invalid column supplied, expected %R, (got %R)",
                        column_cls,
                        p_1
                    );
                    return 0;
                }

                PyObject *p_2 = PyTuple_GET_ITEM(args, 2);
                if (Py_TYPE(p_2) != column_cls)
                {
                    PyErr_Format(
                        PyExc_TypeError,
                        "invalid column supplied, expected %R, (got %R)",
                        column_cls,
                        p_2
                    );
                    return 0;
                }

            glm = new FMatrix3x3Glm(

                    ((FVector3 *)p_0)->glm,

                    ((FVector3 *)p_1)->glm,

                    ((FVector3 *)p_2)->glm

            );

            break;
        }
        case 9:
        {

                float c_0 = 0;

                float c_1 = 0;

                float c_2 = 0;

                float c_3 = 0;

                float c_4 = 0;

                float c_5 = 0;

                float c_6 = 0;

                float c_7 = 0;

                float c_8 = 0;


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

            {
                auto arg = PyTuple_GET_ITEM(args, 4);
                c_4 = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 5);
                c_5 = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 6);
                c_6 = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 7);
                c_7 = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 8);
                c_8 = pyobject_to_c_float(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            glm = new FMatrix3x3Glm(

                    c_0,

                    c_1,

                    c_2,

                    c_3,

                    c_4,

                    c_5,

                    c_6,

                    c_7,

                    c_8

            );
            break;
        }
        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to FMatrix3x3, expected "
                "0, 1, 3 or 9 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    FMatrix3x3 *self = (FMatrix3x3*)cls->tp_alloc(cls, 0);
    if (!self)
    {
        delete glm;
        return 0;
    }
    self->glm = glm;

    return (PyObject *)self;
}


static void
FMatrix3x3__dealloc__(FMatrix3x3 *self)
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
FMatrix3x3__hash__(FMatrix3x3 *self)
{
    Py_ssize_t len = 9;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (FMatrix3x3Glm::length_type c = 0; c < 3; c++)
    {
        for (FMatrix3x3Glm::length_type r = 0; r < 3; r++)
        {
            Py_uhash_t lane = std::hash<float>{}((*self->glm)[r][c]);
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
FMatrix3x3__repr__(FMatrix3x3 *self)
{
    PyObject *result = 0;


        PyObject *py_0_0 = 0;

        PyObject *py_0_1 = 0;

        PyObject *py_0_2 = 0;



        PyObject *py_1_0 = 0;

        PyObject *py_1_1 = 0;

        PyObject *py_1_2 = 0;



        PyObject *py_2_0 = 0;

        PyObject *py_2_1 = 0;

        PyObject *py_2_2 = 0;





        py_0_0 = c_float_to_pyobject((*self->glm)[0][0]);
        if (!py_0_0){ goto cleanup; }

        py_0_1 = c_float_to_pyobject((*self->glm)[1][0]);
        if (!py_0_1){ goto cleanup; }

        py_0_2 = c_float_to_pyobject((*self->glm)[2][0]);
        if (!py_0_2){ goto cleanup; }



        py_1_0 = c_float_to_pyobject((*self->glm)[0][1]);
        if (!py_1_0){ goto cleanup; }

        py_1_1 = c_float_to_pyobject((*self->glm)[1][1]);
        if (!py_1_1){ goto cleanup; }

        py_1_2 = c_float_to_pyobject((*self->glm)[2][1]);
        if (!py_1_2){ goto cleanup; }



        py_2_0 = c_float_to_pyobject((*self->glm)[0][2]);
        if (!py_2_0){ goto cleanup; }

        py_2_1 = c_float_to_pyobject((*self->glm)[1][2]);
        if (!py_2_1){ goto cleanup; }

        py_2_2 = c_float_to_pyobject((*self->glm)[2][2]);
        if (!py_2_2){ goto cleanup; }



    result = PyUnicode_FromFormat(
        "FMatrix3x3("

        "("

            "%R"
            ", "

            "%R"
            ", "

            "%R"


        ")"

        ", "


        "("

            "%R"
            ", "

            "%R"
            ", "

            "%R"


        ")"

        ", "


        "("

            "%R"
            ", "

            "%R"
            ", "

            "%R"


        ")"


        ")",


            py_0_0
            ,

            py_1_0
            ,

            py_2_0
            ,



            py_0_1
            ,

            py_1_1
            ,

            py_2_1
            ,



            py_0_2
            ,

            py_1_2
            ,

            py_2_2



    );
cleanup:


        Py_XDECREF(py_0_0);

        Py_XDECREF(py_0_1);

        Py_XDECREF(py_0_2);



        Py_XDECREF(py_1_0);

        Py_XDECREF(py_1_1);

        Py_XDECREF(py_1_2);



        Py_XDECREF(py_2_0);

        Py_XDECREF(py_2_1);

        Py_XDECREF(py_2_2);


    return result;
}


static Py_ssize_t
FMatrix3x3__len__(FMatrix3x3 *self)
{
    return 3;
}


static PyObject *
FMatrix3x3__getitem__(FMatrix3x3 *self, Py_ssize_t index)
{
    if (index < 0 || index > 2)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    const auto& v = (*self->glm)[(FMatrix3x3Glm::length_type)index];
    return (PyObject *)create_FVector3_from_glm(v);
}


static PyObject *
FMatrix3x3__richcmp__(FMatrix3x3 *self, FMatrix3x3 *other, int op)
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
FMatrix3x3__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3Glm matrix;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        matrix = (*((FMatrix3x3 *)left)->glm) + (*((FMatrix3x3 *)right)->glm);
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((FMatrix3x3 *)left)->glm) + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((FMatrix3x3 *)right)->glm) + c_left;
        }
    }

    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
FMatrix3x3__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3Glm matrix;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        matrix = (*((FMatrix3x3 *)left)->glm) - (*((FMatrix3x3 *)right)->glm);
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_float(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((FMatrix3x3 *)left)->glm) - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_float(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                matrix = c_left - (*((FMatrix3x3 *)right)->glm);

        }
    }

    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
FMatrix3x3__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3Glm matrix;
    if (Py_TYPE(left) == cls)
    {
        auto c_right = pyobject_to_c_float(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = (*((FMatrix3x3 *)left)->glm) * c_right;
    }
    else
    {
        auto c_left = pyobject_to_c_float(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = c_left * (*((FMatrix3x3 *)right)->glm);
    }

    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
FMatrix3x3__matmul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    if (Py_TYPE(left) == cls)
    {



        {
            auto right_cls = module_state->FMatrix2x3_PyTypeObject;
            auto result_cls = module_state->FMatrix2x3_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                FMatrix2x3 *result = (FMatrix2x3 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new FMatrix2x3Glm(
                    (*((FMatrix3x3 *)left)->glm) * (*((FMatrix2x3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }





        {
            auto right_cls = module_state->FMatrix3x3_PyTypeObject;
            auto result_cls = module_state->FMatrix3x3_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                FMatrix3x3 *result = (FMatrix3x3 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new FMatrix3x3Glm(
                    (*((FMatrix3x3 *)left)->glm) * (*((FMatrix3x3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }





        {
            auto right_cls = module_state->FMatrix4x3_PyTypeObject;
            auto result_cls = module_state->FMatrix4x3_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                FMatrix4x3 *result = (FMatrix4x3 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new FMatrix4x3Glm(
                    (*((FMatrix3x3 *)left)->glm) * (*((FMatrix4x3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }






        {
            auto row_cls = module_state->FVector3_PyTypeObject;
            auto column_cls = module_state->FVector3_PyTypeObject;
            if (Py_TYPE(right) == row_cls)
            {
                FVector3 *result = (FVector3 *)column_cls->tp_alloc(column_cls, 0);
                if (!result){ return 0; }
                result->glm = FVector3Glm(
                    (*((FMatrix3x3 *)left)->glm) * (((FVector3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }
    }
    else
    {


        auto row_cls = module_state->FVector3_PyTypeObject;
        auto column_cls = module_state->FVector3_PyTypeObject;
        if (Py_TYPE(left) == column_cls)
        {
            FVector3 *result = (FVector3 *)row_cls->tp_alloc(row_cls, 0);
            if (!result){ return 0; }
            result->glm = FVector3Glm(
                (((FVector3 *)left)->glm) * (*((FMatrix3x3 *)right)->glm)
            );
            return (PyObject *)result;
        }
    }

    Py_RETURN_NOTIMPLEMENTED;
}

static PyObject *
FMatrix3x3__truediv__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3Glm matrix;
    if (Py_TYPE(left) == cls)
    {

        if (Py_TYPE(right) == cls)
        {
            FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
            if (!result){ return 0; }
            result->glm = new FMatrix3x3Glm(
                (*((FMatrix3x3 *)left)->glm) / (*((FMatrix3x3 *)right)->glm)
            );
            return (PyObject *)result;
        }

        {
            auto row_cls = module_state->FVector3_PyTypeObject;
            if (Py_TYPE(right) == row_cls)
            {
                FVector3 *result = (FVector3 *)row_cls->tp_alloc(row_cls, 0);
                if (!result){ return 0; }
                result->glm = FVector3Glm(
                    (*((FMatrix3x3 *)left)->glm) / (((FVector3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }


        auto c_right = pyobject_to_c_float(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = (*((FMatrix3x3 *)left)->glm) / c_right;
    }
    else
    {

        {
            auto row_cls = module_state->FVector3_PyTypeObject;
            if (Py_TYPE(left) == row_cls)
            {
                FVector3 *result = (FVector3 *)row_cls->tp_alloc(row_cls, 0);
                if (!result){ return 0; }
                result->glm = FVector3Glm(
                    (((FVector3 *)left)->glm) / (*((FMatrix3x3 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }


        auto c_left = pyobject_to_c_float(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = c_left / (*((FMatrix3x3 *)right)->glm);
    }

    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
FMatrix3x3__neg__(FMatrix3x3 *self)
{
    auto cls = Py_TYPE(self);

    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(-(*self->glm));

    return (PyObject *)result;
}


static int
FMatrix3x3_getbufferproc(FMatrix3x3 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FMatrix3x3 is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "FMatrix3x3 cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = glm::value_ptr(*self->glm);
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 9;
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
        static Py_ssize_t shape[] = { 3, 3 };
        view->shape = &shape[0];
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


static PyMemberDef FMatrix3x3_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FMatrix3x3, weakreflist), READONLY},
    {0}
};


static PyObject *
FMatrix3x3_address(FMatrix3x3 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
FMatrix3x3_pointer(FMatrix3x3 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyGetSetDef FMatrix3x3_PyGetSetDef[] = {
    {"address", (getter)FMatrix3x3_address, 0, 0, 0},
    {"pointer", (getter)FMatrix3x3_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};



    static FMatrix3x3 *
    FMatrix3x3_inverse(FMatrix3x3 *self, void*)
    {
        auto cls = Py_TYPE(self);
        auto matrix = glm::inverse(*self->glm);
        FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = new FMatrix3x3Glm(matrix);
        return result;
    }







    static FQuaternion *
    FMatrix3x3_to_quaternion(FMatrix3x3 *self, void*)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FQuaternion_PyTypeObject;

        auto *result = (FQuaternion *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = new FQuaternionGlm(glm::quat_cast(*self->glm));
        return result;
    }



static FVector3 *
FMatrix3x3_get_row(FMatrix3x3 *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 1)
    {
        PyErr_Format(PyExc_TypeError, "expected 1 argument, got %zi", nargs);
        return 0;
    }

    auto index = PyLong_AsLong(args[0]);
    if (PyErr_Occurred()){ return 0; }
    if (index < 0 || index > 2)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto row_cls = module_state->FVector3_PyTypeObject;

    auto *result = (FVector3 *)row_cls->tp_alloc(row_cls, 0);
    if (!result){ return 0; }
    auto row = glm::row(*self->glm, index);
    result->glm = FVector3Glm(row);
    return result;
}



static FMatrix3x3 *
FMatrix3x3_transpose(FMatrix3x3 *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3Glm matrix = glm::transpose(*self->glm);
    FMatrix3x3 *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(matrix);
    return result;
}



static PyObject *
FMatrix3x3_get_size(FMatrix3x3 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 9);
}


static PyObject *
FMatrix3x3_get_limits(FMatrix3x3 *self, void *)
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
FMatrix3x3_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float) * 9;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->glm = new FMatrix3x3Glm();
    std::memcpy(result->glm, view.buf, expected_size);
    PyBuffer_Release(&view);
    return (PyObject *)result;
}






    static DMatrix3x3 *
    FMatrix3x3_to_dmatrix(FMatrix3x3 *self, void*)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->DMatrix3x3_PyTypeObject;

        auto *result = (DMatrix3x3 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = new DMatrix3x3Glm(*self->glm);
        return result;
    }



static PyObject *
FMatrix3x3_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->FMatrix3x3Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyMethodDef FMatrix3x3_PyMethodDef[] = {

        {"inverse", (PyCFunction)FMatrix3x3_inverse, METH_NOARGS, 0},



        {"to_quaternion", (PyCFunction)FMatrix3x3_to_quaternion, METH_NOARGS, 0},



        {"to_dmatrix", (PyCFunction)FMatrix3x3_to_dmatrix, METH_NOARGS, 0},

    {"get_row", (PyCFunction)FMatrix3x3_get_row, METH_FASTCALL, 0},
    {"transpose", (PyCFunction)FMatrix3x3_transpose, METH_NOARGS, 0},
    {"get_limits", (PyCFunction)FMatrix3x3_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)FMatrix3x3_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)FMatrix3x3_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)FMatrix3x3_from_buffer, METH_O | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FMatrix3x3_PyType_Slots [] = {
    {Py_tp_new, (void*)FMatrix3x3__new__},
    {Py_tp_dealloc, (void*)FMatrix3x3__dealloc__},
    {Py_tp_hash, (void*)FMatrix3x3__hash__},
    {Py_tp_repr, (void*)FMatrix3x3__repr__},
    {Py_sq_length, (void*)FMatrix3x3__len__},
    {Py_sq_item, (void*)FMatrix3x3__getitem__},
    {Py_tp_richcompare, (void*)FMatrix3x3__richcmp__},
    {Py_nb_add, (void*)FMatrix3x3__add__},
    {Py_nb_subtract, (void*)FMatrix3x3__sub__},
    {Py_nb_multiply, (void*)FMatrix3x3__mul__},
    {Py_nb_matrix_multiply, (void*)FMatrix3x3__matmul__},
    {Py_nb_true_divide, (void*)FMatrix3x3__truediv__},
    {Py_nb_negative, (void*)FMatrix3x3__neg__},
    {Py_bf_getbuffer, (void*)FMatrix3x3_getbufferproc},
    {Py_tp_getset, (void*)FMatrix3x3_PyGetSetDef},
    {Py_tp_members, (void*)FMatrix3x3_PyMemberDef},
    {Py_tp_methods, (void*)FMatrix3x3_PyMethodDef},
    {0, 0},
};


static PyType_Spec FMatrix3x3_PyTypeSpec = {
    "emath.FMatrix3x3",
    sizeof(FMatrix3x3),
    0,
    Py_TPFLAGS_DEFAULT,
    FMatrix3x3_PyType_Slots
};


static PyTypeObject *
define_FMatrix3x3_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FMatrix3x3_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FMatrix3x3", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}



static PyObject *
FMatrix3x3Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FMatrix3x3_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "FMatrix3x3 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (FMatrix3x3Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (FMatrix3x3Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new FMatrix3x3Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = *(((FMatrix3x3*)arg)->glm);
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
FMatrix3x3Array__dealloc__(FMatrix3x3Array *self)
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
FMatrix3x3Array__hash__(FMatrix3x3Array *self)
{
    Py_ssize_t len = self->length * 9;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (FMatrix3x3Glm::length_type c = 0; c < 3; c++)
        {
            for (FMatrix3x3Glm::length_type r = 0; r < 3; r++)
            {
                Py_uhash_t lane = std::hash<float>{}(self->glm[i][r][c]);
                acc += lane * _HASH_XXPRIME_2;
                acc = _HASH_XXROTATE(acc);
                acc *= _HASH_XXPRIME_1;
            }
            acc += len ^ (_HASH_XXPRIME_5 ^ 3527539UL);
        }
    }

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}


static PyObject *
FMatrix3x3Array__repr__(FMatrix3x3Array *self)
{
    return PyUnicode_FromFormat("FMatrix3x3Array[%zu]", self->length);
}


static Py_ssize_t
FMatrix3x3Array__len__(FMatrix3x3Array *self)
{
    return self->length;
}


static PyObject *
FMatrix3x3Array__sq_getitem__(FMatrix3x3Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->FMatrix3x3_PyTypeObject;

    FMatrix3x3 *result = (FMatrix3x3 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
FMatrix3x3Array__mp_getitem__(FMatrix3x3Array *self, PyObject *key)
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
        auto *result = (FMatrix3x3Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new FMatrix3x3Glm[length];
            for (FMatrix3x3Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->FMatrix3x3_PyTypeObject;

        FMatrix3x3 *result = (FMatrix3x3 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = new FMatrix3x3Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
FMatrix3x3Array__richcmp__(
    FMatrix3x3Array *self,
    FMatrix3x3Array *other,
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
FMatrix3x3Array__bool__(FMatrix3x3Array *self)
{
    return self->length ? 1 : 0;
}


static int
FMatrix3x3Array_getbufferproc(FMatrix3x3Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "FMatrix3x3 is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "FMatrix3x3 cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(float) * 9 * self->length;
    view->readonly = 1;
    view->itemsize = sizeof(float);
    view->ndim = 3;
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
        view->shape = new Py_ssize_t[3] {
            (Py_ssize_t)self->length,
            3,
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
            sizeof(float) * 9,
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
FMatrix3x3Array_releasebufferproc(FMatrix3x3Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef FMatrix3x3Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(FMatrix3x3Array, weakreflist), READONLY},
    {0}
};


static PyObject *
FMatrix3x3Array_address(FMatrix3x3Array *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
FMatrix3x3Array_pointer(FMatrix3x3Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_float_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
FMatrix3x3Array_size(FMatrix3x3Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(float) * 9 * self->length);
}


static PyGetSetDef FMatrix3x3Array_PyGetSetDef[] = {
    {"address", (getter)FMatrix3x3Array_address, 0, 0, 0},
    {"pointer", (getter)FMatrix3x3Array_pointer, 0, 0, 0},
    {"size", (getter)FMatrix3x3Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
FMatrix3x3Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(float);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(float) * 9))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(float), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(float) * 9);

    auto *result = (FMatrix3x3Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new FMatrix3x3Glm[array_length];
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
FMatrix3x3Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->FMatrix3x3_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef FMatrix3x3Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)FMatrix3x3Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)FMatrix3x3Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot FMatrix3x3Array_PyType_Slots [] = {
    {Py_tp_new, (void*)FMatrix3x3Array__new__},
    {Py_tp_dealloc, (void*)FMatrix3x3Array__dealloc__},
    {Py_tp_hash, (void*)FMatrix3x3Array__hash__},
    {Py_tp_repr, (void*)FMatrix3x3Array__repr__},
    {Py_sq_length, (void*)FMatrix3x3Array__len__},
    {Py_sq_item, (void*)FMatrix3x3Array__sq_getitem__},
    {Py_mp_subscript, (void*)FMatrix3x3Array__mp_getitem__},
    {Py_tp_richcompare, (void*)FMatrix3x3Array__richcmp__},
    {Py_nb_bool, (void*)FMatrix3x3Array__bool__},
    {Py_bf_getbuffer, (void*)FMatrix3x3Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)FMatrix3x3Array_releasebufferproc},
    {Py_tp_getset, (void*)FMatrix3x3Array_PyGetSetDef},
    {Py_tp_members, (void*)FMatrix3x3Array_PyMemberDef},
    {Py_tp_methods, (void*)FMatrix3x3Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec FMatrix3x3Array_PyTypeSpec = {
    "emath.FMatrix3x3Array",
    sizeof(FMatrix3x3Array),
    0,
    Py_TPFLAGS_DEFAULT,
    FMatrix3x3Array_PyType_Slots
};


static PyTypeObject *
define_FMatrix3x3Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &FMatrix3x3Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "FMatrix3x3Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_FMatrix3x3_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FMatrix3x3_PyTypeObject;
}


static PyTypeObject *
get_FMatrix3x3Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->FMatrix3x3Array_PyTypeObject;
}


static PyObject *
create_FMatrix3x3(const float *value)
{

    auto cls = get_FMatrix3x3_type();
    auto result = (FMatrix3x3 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new FMatrix3x3Glm(*(FMatrix3x3Glm *)value);
    return (PyObject *)result;
}


static PyObject *
create_FMatrix3x3Array(size_t length, const float *value)
{
    auto cls = get_FMatrix3x3Array_type();
    auto result = (FMatrix3x3Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new FMatrix3x3Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((FMatrix3x3Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static float *
get_FMatrix3x3_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FMatrix3x3_type())
    {
        PyErr_Format(PyExc_TypeError, "expected FMatrix3x3, got %R", self);
        return 0;
    }
    return (float *)((FMatrix3x3 *)self)->glm;
}


static float *
get_FMatrix3x3Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_FMatrix3x3Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FMatrix3x3Array, got %R",
            self
        );
        return 0;
    }
    return (float *)((FMatrix3x3Array *)self)->glm;
}


static size_t
get_FMatrix3x3Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_FMatrix3x3Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected FMatrix3x3Array, got %R",
            self
        );
        return 0;
    }
    return ((FMatrix3x3Array *)self)->length;
}

#endif

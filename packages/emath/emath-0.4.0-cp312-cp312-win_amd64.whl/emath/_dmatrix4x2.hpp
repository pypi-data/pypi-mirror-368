
// generated from codegen/templates/_matrix.hpp

#ifndef E_MATH_DMATRIX4X2_HPP
#define E_MATH_DMATRIX4X2_HPP

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
DMatrix4x2__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DMatrix4x2 does accept any keyword arguments"
        );
        return 0;
    }

    DMatrix4x2Glm *glm = 0;
    auto arg_count = PyTuple_GET_SIZE(args);
    switch (PyTuple_GET_SIZE(args))
    {
        case 0:
        {
            glm = new DMatrix4x2Glm();
            break;
        }
        case 1:
        {
            auto arg = PyTuple_GET_ITEM(args, 0);
            double arg_c = pyobject_to_c_double(arg);
            auto error_occurred = PyErr_Occurred();
            if (error_occurred){ return 0; }
            glm = new DMatrix4x2Glm(arg_c);
            break;
        }
        case 4:
        {
            auto module_state = get_module_state();
            if (!module_state){ return 0; }
            auto column_cls = module_state->DVector2_PyTypeObject;

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

                PyObject *p_3 = PyTuple_GET_ITEM(args, 3);
                if (Py_TYPE(p_3) != column_cls)
                {
                    PyErr_Format(
                        PyExc_TypeError,
                        "invalid column supplied, expected %R, (got %R)",
                        column_cls,
                        p_3
                    );
                    return 0;
                }

            glm = new DMatrix4x2Glm(

                    ((DVector2 *)p_0)->glm,

                    ((DVector2 *)p_1)->glm,

                    ((DVector2 *)p_2)->glm,

                    ((DVector2 *)p_3)->glm

            );

            break;
        }
        case 8:
        {

                double c_0 = 0;

                double c_1 = 0;

                double c_2 = 0;

                double c_3 = 0;

                double c_4 = 0;

                double c_5 = 0;

                double c_6 = 0;

                double c_7 = 0;


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

            {
                auto arg = PyTuple_GET_ITEM(args, 4);
                c_4 = pyobject_to_c_double(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 5);
                c_5 = pyobject_to_c_double(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 6);
                c_6 = pyobject_to_c_double(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            {
                auto arg = PyTuple_GET_ITEM(args, 7);
                c_7 = pyobject_to_c_double(arg);
                auto error_occurred = PyErr_Occurred();
                if (error_occurred){ return 0; }
            }

            glm = new DMatrix4x2Glm(

                    c_0,

                    c_1,

                    c_2,

                    c_3,

                    c_4,

                    c_5,

                    c_6,

                    c_7

            );
            break;
        }
        default:
        {
            PyErr_Format(
                PyExc_TypeError,
                "invalid number of arguments supplied to DMatrix4x2, expected "
                "0, 1, 4 or 8 (got %zd)",
                arg_count
            );
            return 0;
        }
    }

    DMatrix4x2 *self = (DMatrix4x2*)cls->tp_alloc(cls, 0);
    if (!self)
    {
        delete glm;
        return 0;
    }
    self->glm = glm;

    return (PyObject *)self;
}


static void
DMatrix4x2__dealloc__(DMatrix4x2 *self)
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
DMatrix4x2__hash__(DMatrix4x2 *self)
{
    Py_ssize_t len = 8;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (DMatrix4x2Glm::length_type c = 0; c < 2; c++)
    {
        for (DMatrix4x2Glm::length_type r = 0; r < 4; r++)
        {
            Py_uhash_t lane = std::hash<double>{}((*self->glm)[r][c]);
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
DMatrix4x2__repr__(DMatrix4x2 *self)
{
    PyObject *result = 0;


        PyObject *py_0_0 = 0;

        PyObject *py_0_1 = 0;

        PyObject *py_0_2 = 0;

        PyObject *py_0_3 = 0;



        PyObject *py_1_0 = 0;

        PyObject *py_1_1 = 0;

        PyObject *py_1_2 = 0;

        PyObject *py_1_3 = 0;





        py_0_0 = c_double_to_pyobject((*self->glm)[0][0]);
        if (!py_0_0){ goto cleanup; }

        py_0_1 = c_double_to_pyobject((*self->glm)[1][0]);
        if (!py_0_1){ goto cleanup; }

        py_0_2 = c_double_to_pyobject((*self->glm)[2][0]);
        if (!py_0_2){ goto cleanup; }

        py_0_3 = c_double_to_pyobject((*self->glm)[3][0]);
        if (!py_0_3){ goto cleanup; }



        py_1_0 = c_double_to_pyobject((*self->glm)[0][1]);
        if (!py_1_0){ goto cleanup; }

        py_1_1 = c_double_to_pyobject((*self->glm)[1][1]);
        if (!py_1_1){ goto cleanup; }

        py_1_2 = c_double_to_pyobject((*self->glm)[2][1]);
        if (!py_1_2){ goto cleanup; }

        py_1_3 = c_double_to_pyobject((*self->glm)[3][1]);
        if (!py_1_3){ goto cleanup; }



    result = PyUnicode_FromFormat(
        "DMatrix4x2("

        "("

            "%R"
            ", "

            "%R"


        ")"

        ", "


        "("

            "%R"
            ", "

            "%R"


        ")"

        ", "


        "("

            "%R"
            ", "

            "%R"


        ")"

        ", "


        "("

            "%R"
            ", "

            "%R"


        ")"


        ")",


            py_0_0
            ,

            py_1_0
            ,



            py_0_1
            ,

            py_1_1
            ,



            py_0_2
            ,

            py_1_2
            ,



            py_0_3
            ,

            py_1_3



    );
cleanup:


        Py_XDECREF(py_0_0);

        Py_XDECREF(py_0_1);

        Py_XDECREF(py_0_2);

        Py_XDECREF(py_0_3);



        Py_XDECREF(py_1_0);

        Py_XDECREF(py_1_1);

        Py_XDECREF(py_1_2);

        Py_XDECREF(py_1_3);


    return result;
}


static Py_ssize_t
DMatrix4x2__len__(DMatrix4x2 *self)
{
    return 4;
}


static PyObject *
DMatrix4x2__getitem__(DMatrix4x2 *self, Py_ssize_t index)
{
    if (index < 0 || index > 3)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    const auto& v = (*self->glm)[(DMatrix4x2Glm::length_type)index];
    return (PyObject *)create_DVector2_from_glm(v);
}


static PyObject *
DMatrix4x2__richcmp__(DMatrix4x2 *self, DMatrix4x2 *other, int op)
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
DMatrix4x2__add__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x2_PyTypeObject;

    DMatrix4x2Glm matrix;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        matrix = (*((DMatrix4x2 *)left)->glm) + (*((DMatrix4x2 *)right)->glm);
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((DMatrix4x2 *)left)->glm) + c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_double(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((DMatrix4x2 *)right)->glm) + c_left;
        }
    }

    DMatrix4x2 *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
DMatrix4x2__sub__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x2_PyTypeObject;

    DMatrix4x2Glm matrix;
    if (Py_TYPE(left) == Py_TYPE(right))
    {
        matrix = (*((DMatrix4x2 *)left)->glm) - (*((DMatrix4x2 *)right)->glm);
    }
    else
    {
        if (Py_TYPE(left) == cls)
        {
            auto c_right = pyobject_to_c_double(right);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
            matrix = (*((DMatrix4x2 *)left)->glm) - c_right;
        }
        else
        {
            auto c_left = pyobject_to_c_double(left);
            if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }

                matrix = DMatrix4x2Glm(

                        c_left,

                        c_left,

                        c_left,

                        c_left,

                        c_left,

                        c_left,

                        c_left,

                        c_left

                ) - (*((DMatrix4x2 *)right)->glm);

        }
    }

    DMatrix4x2 *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
DMatrix4x2__mul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x2_PyTypeObject;

    DMatrix4x2Glm matrix;
    if (Py_TYPE(left) == cls)
    {
        auto c_right = pyobject_to_c_double(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = (*((DMatrix4x2 *)left)->glm) * c_right;
    }
    else
    {
        auto c_left = pyobject_to_c_double(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = c_left * (*((DMatrix4x2 *)right)->glm);
    }

    DMatrix4x2 *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
DMatrix4x2__matmul__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x2_PyTypeObject;

    if (Py_TYPE(left) == cls)
    {



        {
            auto right_cls = module_state->DMatrix2x4_PyTypeObject;
            auto result_cls = module_state->DMatrix2x2_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                DMatrix2x2 *result = (DMatrix2x2 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new DMatrix2x2Glm(
                    (*((DMatrix4x2 *)left)->glm) * (*((DMatrix2x4 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }





        {
            auto right_cls = module_state->DMatrix3x4_PyTypeObject;
            auto result_cls = module_state->DMatrix3x2_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                DMatrix3x2 *result = (DMatrix3x2 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new DMatrix3x2Glm(
                    (*((DMatrix4x2 *)left)->glm) * (*((DMatrix3x4 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }





        {
            auto right_cls = module_state->DMatrix4x4_PyTypeObject;
            auto result_cls = module_state->DMatrix4x2_PyTypeObject;
            if (Py_TYPE(right) == right_cls)
            {
                DMatrix4x2 *result = (DMatrix4x2 *)result_cls->tp_alloc(result_cls, 0);
                if (!result){ return 0; }
                result->glm = new DMatrix4x2Glm(
                    (*((DMatrix4x2 *)left)->glm) * (*((DMatrix4x4 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }






        {
            auto row_cls = module_state->DVector4_PyTypeObject;
            auto column_cls = module_state->DVector2_PyTypeObject;
            if (Py_TYPE(right) == row_cls)
            {
                DVector2 *result = (DVector2 *)column_cls->tp_alloc(column_cls, 0);
                if (!result){ return 0; }
                result->glm = DVector2Glm(
                    (*((DMatrix4x2 *)left)->glm) * (((DVector4 *)right)->glm)
                );
                return (PyObject *)result;
            }
        }
    }
    else
    {


        auto row_cls = module_state->DVector4_PyTypeObject;
        auto column_cls = module_state->DVector2_PyTypeObject;
        if (Py_TYPE(left) == column_cls)
        {
            DVector4 *result = (DVector4 *)row_cls->tp_alloc(row_cls, 0);
            if (!result){ return 0; }
            result->glm = DVector4Glm(
                (((DVector2 *)left)->glm) * (*((DMatrix4x2 *)right)->glm)
            );
            return (PyObject *)result;
        }
    }

    Py_RETURN_NOTIMPLEMENTED;
}

static PyObject *
DMatrix4x2__truediv__(PyObject *left, PyObject *right)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix4x2_PyTypeObject;

    DMatrix4x2Glm matrix;
    if (Py_TYPE(left) == cls)
    {


        auto c_right = pyobject_to_c_double(right);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = (*((DMatrix4x2 *)left)->glm) / c_right;
    }
    else
    {


        auto c_left = pyobject_to_c_double(left);
        if (PyErr_Occurred()){ PyErr_Clear(); Py_RETURN_NOTIMPLEMENTED; }
        matrix = c_left / (*((DMatrix4x2 *)right)->glm);
    }

    DMatrix4x2 *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(matrix);

    return (PyObject *)result;
}


static PyObject *
DMatrix4x2__neg__(DMatrix4x2 *self)
{
    auto cls = Py_TYPE(self);

    DMatrix4x2 *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(-(*self->glm));

    return (PyObject *)result;
}


static int
DMatrix4x2_getbufferproc(DMatrix4x2 *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "DMatrix4x2 is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "DMatrix4x2 cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = glm::value_ptr(*self->glm);
    view->obj = (PyObject *)self;
    view->len = sizeof(double) * 8;
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
        static Py_ssize_t shape[] = { 4, 2 };
        view->shape = &shape[0];
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        static Py_ssize_t strides[] = {
            sizeof(double) * 2,
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


static PyMemberDef DMatrix4x2_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DMatrix4x2, weakreflist), READONLY},
    {0}
};


static PyObject *
DMatrix4x2_address(DMatrix4x2 *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
DMatrix4x2_pointer(DMatrix4x2 *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_double_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyGetSetDef DMatrix4x2_PyGetSetDef[] = {
    {"address", (getter)DMatrix4x2_address, 0, 0, 0},
    {"pointer", (getter)DMatrix4x2_pointer, 0, 0, 0},
    {0, 0, 0, 0, 0}
};











static DVector4 *
DMatrix4x2_get_row(DMatrix4x2 *self, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 1)
    {
        PyErr_Format(PyExc_TypeError, "expected 1 argument, got %zi", nargs);
        return 0;
    }

    auto index = PyLong_AsLong(args[0]);
    if (PyErr_Occurred()){ return 0; }
    if (index < 0 || index > 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto row_cls = module_state->DVector4_PyTypeObject;

    auto *result = (DVector4 *)row_cls->tp_alloc(row_cls, 0);
    if (!result){ return 0; }
    auto row = glm::row(*self->glm, index);
    result->glm = DVector4Glm(row);
    return result;
}



static DMatrix2x4 *
DMatrix4x2_transpose(DMatrix4x2 *self, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto cls = module_state->DMatrix2x4_PyTypeObject;

    DMatrix2x4Glm matrix = glm::transpose(*self->glm);
    DMatrix2x4 *result = (DMatrix2x4 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix2x4Glm(matrix);
    return result;
}



static PyObject *
DMatrix4x2_get_size(DMatrix4x2 *cls, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 8);
}


static PyObject *
DMatrix4x2_get_limits(DMatrix4x2 *self, void *)
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
DMatrix4x2_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(double) * 8;
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length < expected_size)
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer of size %zd, got %zd", expected_size, view_length);
        return 0;
    }

    auto *result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->glm = new DMatrix4x2Glm();
    std::memcpy(result->glm, view.buf, expected_size);
    PyBuffer_Release(&view);
    return (PyObject *)result;
}



    static FMatrix4x2 *
    DMatrix4x2_to_fmatrix(DMatrix4x2 *self, void*)
    {
        auto module_state = get_module_state();
        if (!module_state){ return 0; }
        auto cls = module_state->FMatrix4x2_PyTypeObject;

        auto *result = (FMatrix4x2 *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        result->glm = new FMatrix4x2Glm(*self->glm);
        return result;
    }






static PyObject *
DMatrix4x2_get_array_type(PyTypeObject *cls, void*)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto array_type = module_state->DMatrix4x2Array_PyTypeObject;
    Py_INCREF(array_type);
    return (PyObject *)array_type;
}


static PyMethodDef DMatrix4x2_PyMethodDef[] = {




        {"to_fmatrix", (PyCFunction)DMatrix4x2_to_fmatrix, METH_NOARGS, 0},


    {"get_row", (PyCFunction)DMatrix4x2_get_row, METH_FASTCALL, 0},
    {"transpose", (PyCFunction)DMatrix4x2_transpose, METH_NOARGS, 0},
    {"get_limits", (PyCFunction)DMatrix4x2_get_limits, METH_NOARGS | METH_STATIC, 0},
    {"get_size", (PyCFunction)DMatrix4x2_get_size, METH_NOARGS | METH_STATIC, 0},
    {"get_array_type", (PyCFunction)DMatrix4x2_get_array_type, METH_NOARGS | METH_STATIC, 0},
    {"from_buffer", (PyCFunction)DMatrix4x2_from_buffer, METH_O | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot DMatrix4x2_PyType_Slots [] = {
    {Py_tp_new, (void*)DMatrix4x2__new__},
    {Py_tp_dealloc, (void*)DMatrix4x2__dealloc__},
    {Py_tp_hash, (void*)DMatrix4x2__hash__},
    {Py_tp_repr, (void*)DMatrix4x2__repr__},
    {Py_sq_length, (void*)DMatrix4x2__len__},
    {Py_sq_item, (void*)DMatrix4x2__getitem__},
    {Py_tp_richcompare, (void*)DMatrix4x2__richcmp__},
    {Py_nb_add, (void*)DMatrix4x2__add__},
    {Py_nb_subtract, (void*)DMatrix4x2__sub__},
    {Py_nb_multiply, (void*)DMatrix4x2__mul__},
    {Py_nb_matrix_multiply, (void*)DMatrix4x2__matmul__},
    {Py_nb_true_divide, (void*)DMatrix4x2__truediv__},
    {Py_nb_negative, (void*)DMatrix4x2__neg__},
    {Py_bf_getbuffer, (void*)DMatrix4x2_getbufferproc},
    {Py_tp_getset, (void*)DMatrix4x2_PyGetSetDef},
    {Py_tp_members, (void*)DMatrix4x2_PyMemberDef},
    {Py_tp_methods, (void*)DMatrix4x2_PyMethodDef},
    {0, 0},
};


static PyType_Spec DMatrix4x2_PyTypeSpec = {
    "emath.DMatrix4x2",
    sizeof(DMatrix4x2),
    0,
    Py_TPFLAGS_DEFAULT,
    DMatrix4x2_PyType_Slots
};


static PyTypeObject *
define_DMatrix4x2_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DMatrix4x2_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DMatrix4x2", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}



static PyObject *
DMatrix4x2Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DMatrix4x2_PyTypeObject;

    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "DMatrix4x2 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (DMatrix4x2Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->glm = 0;
        return (PyObject *)self;
    }

    auto *self = (DMatrix4x2Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->glm = new DMatrix4x2Glm[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        if (Py_TYPE(arg) == element_cls)
        {
            self->glm[i] = *(((DMatrix4x2*)arg)->glm);
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
DMatrix4x2Array__dealloc__(DMatrix4x2Array *self)
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
DMatrix4x2Array__hash__(DMatrix4x2Array *self)
{
    Py_ssize_t len = self->length * 8;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        for (DMatrix4x2Glm::length_type c = 0; c < 2; c++)
        {
            for (DMatrix4x2Glm::length_type r = 0; r < 4; r++)
            {
                Py_uhash_t lane = std::hash<double>{}(self->glm[i][r][c]);
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
DMatrix4x2Array__repr__(DMatrix4x2Array *self)
{
    return PyUnicode_FromFormat("DMatrix4x2Array[%zu]", self->length);
}


static Py_ssize_t
DMatrix4x2Array__len__(DMatrix4x2Array *self)
{
    return self->length;
}


static PyObject *
DMatrix4x2Array__sq_getitem__(DMatrix4x2Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }

    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto element_cls = module_state->DMatrix4x2_PyTypeObject;

    DMatrix4x2 *result = (DMatrix4x2 *)element_cls->tp_alloc(element_cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(self->glm[index]);

    return (PyObject *)result;
}


static PyObject *
DMatrix4x2Array__mp_getitem__(DMatrix4x2Array *self, PyObject *key)
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
        auto *result = (DMatrix4x2Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->glm = 0;
        }
        else
        {
            result->length = length;
            result->glm = new DMatrix4x2Glm[length];
            for (DMatrix4x2Glm::length_type i = 0; i < length; i++)
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
        auto element_cls = module_state->DMatrix4x2_PyTypeObject;

        DMatrix4x2 *result = (DMatrix4x2 *)element_cls->tp_alloc(element_cls, 0);
        if (!result){ return 0; }
        result->glm = new DMatrix4x2Glm(self->glm[index]);

        return (PyObject *)result;
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
DMatrix4x2Array__richcmp__(
    DMatrix4x2Array *self,
    DMatrix4x2Array *other,
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
DMatrix4x2Array__bool__(DMatrix4x2Array *self)
{
    return self->length ? 1 : 0;
}


static int
DMatrix4x2Array_getbufferproc(DMatrix4x2Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "DMatrix4x2 is read only");
        view->obj = 0;
        return -1;
    }
    if ((!(flags & PyBUF_C_CONTIGUOUS)) && flags & PyBUF_F_CONTIGUOUS)
    {
        PyErr_SetString(PyExc_BufferError, "DMatrix4x2 cannot be made Fortran contiguous");
        view->obj = 0;
        return -1;
    }
    view->buf = self->glm;
    view->obj = (PyObject *)self;
    view->len = sizeof(double) * 8 * self->length;
    view->readonly = 1;
    view->itemsize = sizeof(double);
    view->ndim = 3;
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
        view->shape = new Py_ssize_t[3] {
            (Py_ssize_t)self->length,
            4,
            2
        };
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        static Py_ssize_t strides[] = {
            sizeof(double) * 8,
            sizeof(double) * 2,
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
DMatrix4x2Array_releasebufferproc(DMatrix4x2Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef DMatrix4x2Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(DMatrix4x2Array, weakreflist), READONLY},
    {0}
};


static PyObject *
DMatrix4x2Array_address(DMatrix4x2Array *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->glm);
}


static PyObject *
DMatrix4x2Array_pointer(DMatrix4x2Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_double_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->glm);
}


static PyObject *
DMatrix4x2Array_size(DMatrix4x2Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(double) * 8 * self->length);
}


static PyGetSetDef DMatrix4x2Array_PyGetSetDef[] = {
    {"address", (getter)DMatrix4x2Array_address, 0, 0, 0},
    {"pointer", (getter)DMatrix4x2Array_pointer, 0, 0, 0},
    {"size", (getter)DMatrix4x2Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
DMatrix4x2Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(double);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % (sizeof(double) * 8))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(double), view_length);
        return 0;
    }
    auto array_length = view_length / (sizeof(double) * 8);

    auto *result = (DMatrix4x2Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->glm = new DMatrix4x2Glm[array_length];
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
DMatrix4x2Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto component_type = module_state->DMatrix4x2_PyTypeObject;
    Py_INCREF(component_type);
    return (PyObject *)component_type;
}


static PyMethodDef DMatrix4x2Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)DMatrix4x2Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)DMatrix4x2Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot DMatrix4x2Array_PyType_Slots [] = {
    {Py_tp_new, (void*)DMatrix4x2Array__new__},
    {Py_tp_dealloc, (void*)DMatrix4x2Array__dealloc__},
    {Py_tp_hash, (void*)DMatrix4x2Array__hash__},
    {Py_tp_repr, (void*)DMatrix4x2Array__repr__},
    {Py_sq_length, (void*)DMatrix4x2Array__len__},
    {Py_sq_item, (void*)DMatrix4x2Array__sq_getitem__},
    {Py_mp_subscript, (void*)DMatrix4x2Array__mp_getitem__},
    {Py_tp_richcompare, (void*)DMatrix4x2Array__richcmp__},
    {Py_nb_bool, (void*)DMatrix4x2Array__bool__},
    {Py_bf_getbuffer, (void*)DMatrix4x2Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)DMatrix4x2Array_releasebufferproc},
    {Py_tp_getset, (void*)DMatrix4x2Array_PyGetSetDef},
    {Py_tp_members, (void*)DMatrix4x2Array_PyMemberDef},
    {Py_tp_methods, (void*)DMatrix4x2Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec DMatrix4x2Array_PyTypeSpec = {
    "emath.DMatrix4x2Array",
    sizeof(DMatrix4x2Array),
    0,
    Py_TPFLAGS_DEFAULT,
    DMatrix4x2Array_PyType_Slots
};


static PyTypeObject *
define_DMatrix4x2Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &DMatrix4x2Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "DMatrix4x2Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_DMatrix4x2_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DMatrix4x2_PyTypeObject;
}


static PyTypeObject *
get_DMatrix4x2Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->DMatrix4x2Array_PyTypeObject;
}


static PyObject *
create_DMatrix4x2(const double *value)
{

    auto cls = get_DMatrix4x2_type();
    auto result = (DMatrix4x2 *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->glm = new DMatrix4x2Glm(*(DMatrix4x2Glm *)value);
    return (PyObject *)result;
}


static PyObject *
create_DMatrix4x2Array(size_t length, const double *value)
{
    auto cls = get_DMatrix4x2Array_type();
    auto result = (DMatrix4x2Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->glm = new DMatrix4x2Glm[length];
        for (size_t i = 0; i < length; i++)
        {
            result->glm[i] = ((DMatrix4x2Glm *)value)[i];
        }
    }
    else
    {
        result->glm = 0;
    }
    return (PyObject *)result;
}


static double *
get_DMatrix4x2_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DMatrix4x2_type())
    {
        PyErr_Format(PyExc_TypeError, "expected DMatrix4x2, got %R", self);
        return 0;
    }
    return (double *)((DMatrix4x2 *)self)->glm;
}


static double *
get_DMatrix4x2Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_DMatrix4x2Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DMatrix4x2Array, got %R",
            self
        );
        return 0;
    }
    return (double *)((DMatrix4x2Array *)self)->glm;
}


static size_t
get_DMatrix4x2Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_DMatrix4x2Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected DMatrix4x2Array, got %R",
            self
        );
        return 0;
    }
    return ((DMatrix4x2Array *)self)->length;
}

#endif

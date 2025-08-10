
// generated from codegen/templates/_math.cpp

// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#include "_modulestate.hpp"

    #include "_bvector1.hpp"

    #include "_dvector1.hpp"

    #include "_fvector1.hpp"

    #include "_i8vector1.hpp"

    #include "_u8vector1.hpp"

    #include "_i16vector1.hpp"

    #include "_u16vector1.hpp"

    #include "_i32vector1.hpp"

    #include "_u32vector1.hpp"

    #include "_ivector1.hpp"

    #include "_uvector1.hpp"

    #include "_i64vector1.hpp"

    #include "_u64vector1.hpp"

    #include "_bvector2.hpp"

    #include "_dvector2.hpp"

    #include "_fvector2.hpp"

    #include "_i8vector2.hpp"

    #include "_u8vector2.hpp"

    #include "_i16vector2.hpp"

    #include "_u16vector2.hpp"

    #include "_i32vector2.hpp"

    #include "_u32vector2.hpp"

    #include "_ivector2.hpp"

    #include "_uvector2.hpp"

    #include "_i64vector2.hpp"

    #include "_u64vector2.hpp"

    #include "_bvector3.hpp"

    #include "_dvector3.hpp"

    #include "_fvector3.hpp"

    #include "_i8vector3.hpp"

    #include "_u8vector3.hpp"

    #include "_i16vector3.hpp"

    #include "_u16vector3.hpp"

    #include "_i32vector3.hpp"

    #include "_u32vector3.hpp"

    #include "_ivector3.hpp"

    #include "_uvector3.hpp"

    #include "_i64vector3.hpp"

    #include "_u64vector3.hpp"

    #include "_bvector4.hpp"

    #include "_dvector4.hpp"

    #include "_fvector4.hpp"

    #include "_i8vector4.hpp"

    #include "_u8vector4.hpp"

    #include "_i16vector4.hpp"

    #include "_u16vector4.hpp"

    #include "_i32vector4.hpp"

    #include "_u32vector4.hpp"

    #include "_ivector4.hpp"

    #include "_uvector4.hpp"

    #include "_i64vector4.hpp"

    #include "_u64vector4.hpp"


    #include "_dmatrix2x2.hpp"

    #include "_fmatrix2x2.hpp"

    #include "_dmatrix2x3.hpp"

    #include "_fmatrix2x3.hpp"

    #include "_dmatrix2x4.hpp"

    #include "_fmatrix2x4.hpp"

    #include "_dmatrix3x2.hpp"

    #include "_fmatrix3x2.hpp"

    #include "_dmatrix3x3.hpp"

    #include "_fmatrix3x3.hpp"

    #include "_dmatrix3x4.hpp"

    #include "_fmatrix3x4.hpp"

    #include "_dmatrix4x2.hpp"

    #include "_fmatrix4x2.hpp"

    #include "_dmatrix4x3.hpp"

    #include "_fmatrix4x3.hpp"

    #include "_dmatrix4x4.hpp"

    #include "_fmatrix4x4.hpp"


    #include "_dquaternion.hpp"

    #include "_fquaternion.hpp"


    #include "_b.hpp"

    #include "_d.hpp"

    #include "_f.hpp"

    #include "_i8.hpp"

    #include "_u8.hpp"

    #include "_i16.hpp"

    #include "_u16.hpp"

    #include "_i32.hpp"

    #include "_u32.hpp"

    #include "_i.hpp"

    #include "_u.hpp"

    #include "_i64.hpp"

    #include "_u64.hpp"

#include "emath.h"


static PyMethodDef module_methods[] = {
    {0, 0, 0, 0}
};


static int
module_traverse(PyObject *self, visitproc visit, void *arg)
{
    ModuleState *state = (ModuleState *)PyModule_GetState(self);
    return ModuleState_traverse(state, visit, arg);
}


static int
module_clear(PyObject *self)
{
    ModuleState *state = (ModuleState *)PyModule_GetState(self);
    return ModuleState_clear(state);
}


static struct PyModuleDef module_PyModuleDef = {
    PyModuleDef_HEAD_INIT,
    "emath._emath",
    0,
    sizeof(struct ModuleState),
    module_methods,
    0,
    module_traverse,
    module_clear
};


static void
api_destructor(PyObject *capsule)
{
    EMathApi* api = (EMathApi*)PyCapsule_GetPointer(
        capsule,
        "emath._emath._api"
    );
    delete api;
}


PyMODINIT_FUNC
PyInit__emath()
{
    auto api = new EMathApi{ 0 };
    auto api_capsule = PyCapsule_New(
        (void *)api,
        "emath._emath._api",
        NULL
    );

    PyObject *module = PyModule_Create(&module_PyModuleDef);
    ModuleState *state = 0;
    if (!module){ goto error; }
    if (PyState_AddModule(module, &module_PyModuleDef) == -1){ goto error; }
    state = (ModuleState *)PyModule_GetState(module);

    {
        PyObject *ctypes = PyImport_ImportModule("ctypes");
        if (!ctypes){ goto error; }

        {
            auto c_cast = PyObject_GetAttrString(ctypes, "cast");
            if (!c_cast)
            {
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_cast = c_cast;
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_void_p");
            if (!c_type)
            {
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_void_p = c_type;
        }

        PyObject *ctypes_pointer = PyObject_GetAttrString(ctypes, "POINTER");
        if (!ctypes_pointer)
        {
            Py_DECREF(ctypes);
            goto error;
        }


        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_bool");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_bool_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_bool_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_int8");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_int8_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_int8_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_uint8");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_uint8_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_uint8_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_int16");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_int16_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_int16_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_uint16");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_uint16_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_uint16_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_int32");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_int32_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_int32_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_uint32");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_uint32_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_uint32_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_int64");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_int64_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_int64_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_uint64");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_uint64_t_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_uint64_t_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_int");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_int_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_int_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_uint");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_unsigned_int_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_unsigned_int_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_float");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_float_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_float_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }

        {
            auto c_type = PyObject_GetAttrString(ctypes, "c_double");
            if (!c_type)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
            state->ctypes_c_double_p = PyObject_CallFunction(ctypes_pointer, "O", c_type);
            if (!state->ctypes_c_double_p)
            {
                Py_DECREF(ctypes_pointer);
                Py_DECREF(ctypes);
                goto error;
            }
        }


        Py_DECREF(ctypes_pointer);
        Py_DECREF(ctypes);
    }


        {
            PyTypeObject *type = define_BVector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_BVector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector1Array_PyTypeObject = type;
        }
        api->BVector1_GetType = get_BVector1_type;
        api->BVector1Array_GetType = get_BVector1Array_type;
        api->BVector1_Create = create_BVector1;
        api->BVector1Array_Create = create_BVector1Array;
        api->BVector1_GetValuePointer = get_BVector1_value_ptr;
        api->BVector1Array_GetValuePointer = get_BVector1Array_value_ptr;
        api->BVector1Array_GetLength = get_BVector1Array_length;

        {
            PyTypeObject *type = define_DVector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DVector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector1Array_PyTypeObject = type;
        }
        api->DVector1_GetType = get_DVector1_type;
        api->DVector1Array_GetType = get_DVector1Array_type;
        api->DVector1_Create = create_DVector1;
        api->DVector1Array_Create = create_DVector1Array;
        api->DVector1_GetValuePointer = get_DVector1_value_ptr;
        api->DVector1Array_GetValuePointer = get_DVector1Array_value_ptr;
        api->DVector1Array_GetLength = get_DVector1Array_length;

        {
            PyTypeObject *type = define_FVector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FVector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector1Array_PyTypeObject = type;
        }
        api->FVector1_GetType = get_FVector1_type;
        api->FVector1Array_GetType = get_FVector1Array_type;
        api->FVector1_Create = create_FVector1;
        api->FVector1Array_Create = create_FVector1Array;
        api->FVector1_GetValuePointer = get_FVector1_value_ptr;
        api->FVector1Array_GetValuePointer = get_FVector1Array_value_ptr;
        api->FVector1Array_GetLength = get_FVector1Array_length;

        {
            PyTypeObject *type = define_I8Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I8Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector1Array_PyTypeObject = type;
        }
        api->I8Vector1_GetType = get_I8Vector1_type;
        api->I8Vector1Array_GetType = get_I8Vector1Array_type;
        api->I8Vector1_Create = create_I8Vector1;
        api->I8Vector1Array_Create = create_I8Vector1Array;
        api->I8Vector1_GetValuePointer = get_I8Vector1_value_ptr;
        api->I8Vector1Array_GetValuePointer = get_I8Vector1Array_value_ptr;
        api->I8Vector1Array_GetLength = get_I8Vector1Array_length;

        {
            PyTypeObject *type = define_U8Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U8Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector1Array_PyTypeObject = type;
        }
        api->U8Vector1_GetType = get_U8Vector1_type;
        api->U8Vector1Array_GetType = get_U8Vector1Array_type;
        api->U8Vector1_Create = create_U8Vector1;
        api->U8Vector1Array_Create = create_U8Vector1Array;
        api->U8Vector1_GetValuePointer = get_U8Vector1_value_ptr;
        api->U8Vector1Array_GetValuePointer = get_U8Vector1Array_value_ptr;
        api->U8Vector1Array_GetLength = get_U8Vector1Array_length;

        {
            PyTypeObject *type = define_I16Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I16Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector1Array_PyTypeObject = type;
        }
        api->I16Vector1_GetType = get_I16Vector1_type;
        api->I16Vector1Array_GetType = get_I16Vector1Array_type;
        api->I16Vector1_Create = create_I16Vector1;
        api->I16Vector1Array_Create = create_I16Vector1Array;
        api->I16Vector1_GetValuePointer = get_I16Vector1_value_ptr;
        api->I16Vector1Array_GetValuePointer = get_I16Vector1Array_value_ptr;
        api->I16Vector1Array_GetLength = get_I16Vector1Array_length;

        {
            PyTypeObject *type = define_U16Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U16Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector1Array_PyTypeObject = type;
        }
        api->U16Vector1_GetType = get_U16Vector1_type;
        api->U16Vector1Array_GetType = get_U16Vector1Array_type;
        api->U16Vector1_Create = create_U16Vector1;
        api->U16Vector1Array_Create = create_U16Vector1Array;
        api->U16Vector1_GetValuePointer = get_U16Vector1_value_ptr;
        api->U16Vector1Array_GetValuePointer = get_U16Vector1Array_value_ptr;
        api->U16Vector1Array_GetLength = get_U16Vector1Array_length;

        {
            PyTypeObject *type = define_I32Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I32Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector1Array_PyTypeObject = type;
        }
        api->I32Vector1_GetType = get_I32Vector1_type;
        api->I32Vector1Array_GetType = get_I32Vector1Array_type;
        api->I32Vector1_Create = create_I32Vector1;
        api->I32Vector1Array_Create = create_I32Vector1Array;
        api->I32Vector1_GetValuePointer = get_I32Vector1_value_ptr;
        api->I32Vector1Array_GetValuePointer = get_I32Vector1Array_value_ptr;
        api->I32Vector1Array_GetLength = get_I32Vector1Array_length;

        {
            PyTypeObject *type = define_U32Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U32Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector1Array_PyTypeObject = type;
        }
        api->U32Vector1_GetType = get_U32Vector1_type;
        api->U32Vector1Array_GetType = get_U32Vector1Array_type;
        api->U32Vector1_Create = create_U32Vector1;
        api->U32Vector1Array_Create = create_U32Vector1Array;
        api->U32Vector1_GetValuePointer = get_U32Vector1_value_ptr;
        api->U32Vector1Array_GetValuePointer = get_U32Vector1Array_value_ptr;
        api->U32Vector1Array_GetLength = get_U32Vector1Array_length;

        {
            PyTypeObject *type = define_IVector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_IVector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector1Array_PyTypeObject = type;
        }
        api->IVector1_GetType = get_IVector1_type;
        api->IVector1Array_GetType = get_IVector1Array_type;
        api->IVector1_Create = create_IVector1;
        api->IVector1Array_Create = create_IVector1Array;
        api->IVector1_GetValuePointer = get_IVector1_value_ptr;
        api->IVector1Array_GetValuePointer = get_IVector1Array_value_ptr;
        api->IVector1Array_GetLength = get_IVector1Array_length;

        {
            PyTypeObject *type = define_UVector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_UVector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector1Array_PyTypeObject = type;
        }
        api->UVector1_GetType = get_UVector1_type;
        api->UVector1Array_GetType = get_UVector1Array_type;
        api->UVector1_Create = create_UVector1;
        api->UVector1Array_Create = create_UVector1Array;
        api->UVector1_GetValuePointer = get_UVector1_value_ptr;
        api->UVector1Array_GetValuePointer = get_UVector1Array_value_ptr;
        api->UVector1Array_GetLength = get_UVector1Array_length;

        {
            PyTypeObject *type = define_I64Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I64Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector1Array_PyTypeObject = type;
        }
        api->I64Vector1_GetType = get_I64Vector1_type;
        api->I64Vector1Array_GetType = get_I64Vector1Array_type;
        api->I64Vector1_Create = create_I64Vector1;
        api->I64Vector1Array_Create = create_I64Vector1Array;
        api->I64Vector1_GetValuePointer = get_I64Vector1_value_ptr;
        api->I64Vector1Array_GetValuePointer = get_I64Vector1Array_value_ptr;
        api->I64Vector1Array_GetLength = get_I64Vector1Array_length;

        {
            PyTypeObject *type = define_U64Vector1_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector1_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U64Vector1Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector1Array_PyTypeObject = type;
        }
        api->U64Vector1_GetType = get_U64Vector1_type;
        api->U64Vector1Array_GetType = get_U64Vector1Array_type;
        api->U64Vector1_Create = create_U64Vector1;
        api->U64Vector1Array_Create = create_U64Vector1Array;
        api->U64Vector1_GetValuePointer = get_U64Vector1_value_ptr;
        api->U64Vector1Array_GetValuePointer = get_U64Vector1Array_value_ptr;
        api->U64Vector1Array_GetLength = get_U64Vector1Array_length;

        {
            PyTypeObject *type = define_BVector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_BVector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector2Array_PyTypeObject = type;
        }
        api->BVector2_GetType = get_BVector2_type;
        api->BVector2Array_GetType = get_BVector2Array_type;
        api->BVector2_Create = create_BVector2;
        api->BVector2Array_Create = create_BVector2Array;
        api->BVector2_GetValuePointer = get_BVector2_value_ptr;
        api->BVector2Array_GetValuePointer = get_BVector2Array_value_ptr;
        api->BVector2Array_GetLength = get_BVector2Array_length;

        {
            PyTypeObject *type = define_DVector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DVector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector2Array_PyTypeObject = type;
        }
        api->DVector2_GetType = get_DVector2_type;
        api->DVector2Array_GetType = get_DVector2Array_type;
        api->DVector2_Create = create_DVector2;
        api->DVector2Array_Create = create_DVector2Array;
        api->DVector2_GetValuePointer = get_DVector2_value_ptr;
        api->DVector2Array_GetValuePointer = get_DVector2Array_value_ptr;
        api->DVector2Array_GetLength = get_DVector2Array_length;

        {
            PyTypeObject *type = define_FVector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FVector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector2Array_PyTypeObject = type;
        }
        api->FVector2_GetType = get_FVector2_type;
        api->FVector2Array_GetType = get_FVector2Array_type;
        api->FVector2_Create = create_FVector2;
        api->FVector2Array_Create = create_FVector2Array;
        api->FVector2_GetValuePointer = get_FVector2_value_ptr;
        api->FVector2Array_GetValuePointer = get_FVector2Array_value_ptr;
        api->FVector2Array_GetLength = get_FVector2Array_length;

        {
            PyTypeObject *type = define_I8Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I8Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector2Array_PyTypeObject = type;
        }
        api->I8Vector2_GetType = get_I8Vector2_type;
        api->I8Vector2Array_GetType = get_I8Vector2Array_type;
        api->I8Vector2_Create = create_I8Vector2;
        api->I8Vector2Array_Create = create_I8Vector2Array;
        api->I8Vector2_GetValuePointer = get_I8Vector2_value_ptr;
        api->I8Vector2Array_GetValuePointer = get_I8Vector2Array_value_ptr;
        api->I8Vector2Array_GetLength = get_I8Vector2Array_length;

        {
            PyTypeObject *type = define_U8Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U8Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector2Array_PyTypeObject = type;
        }
        api->U8Vector2_GetType = get_U8Vector2_type;
        api->U8Vector2Array_GetType = get_U8Vector2Array_type;
        api->U8Vector2_Create = create_U8Vector2;
        api->U8Vector2Array_Create = create_U8Vector2Array;
        api->U8Vector2_GetValuePointer = get_U8Vector2_value_ptr;
        api->U8Vector2Array_GetValuePointer = get_U8Vector2Array_value_ptr;
        api->U8Vector2Array_GetLength = get_U8Vector2Array_length;

        {
            PyTypeObject *type = define_I16Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I16Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector2Array_PyTypeObject = type;
        }
        api->I16Vector2_GetType = get_I16Vector2_type;
        api->I16Vector2Array_GetType = get_I16Vector2Array_type;
        api->I16Vector2_Create = create_I16Vector2;
        api->I16Vector2Array_Create = create_I16Vector2Array;
        api->I16Vector2_GetValuePointer = get_I16Vector2_value_ptr;
        api->I16Vector2Array_GetValuePointer = get_I16Vector2Array_value_ptr;
        api->I16Vector2Array_GetLength = get_I16Vector2Array_length;

        {
            PyTypeObject *type = define_U16Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U16Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector2Array_PyTypeObject = type;
        }
        api->U16Vector2_GetType = get_U16Vector2_type;
        api->U16Vector2Array_GetType = get_U16Vector2Array_type;
        api->U16Vector2_Create = create_U16Vector2;
        api->U16Vector2Array_Create = create_U16Vector2Array;
        api->U16Vector2_GetValuePointer = get_U16Vector2_value_ptr;
        api->U16Vector2Array_GetValuePointer = get_U16Vector2Array_value_ptr;
        api->U16Vector2Array_GetLength = get_U16Vector2Array_length;

        {
            PyTypeObject *type = define_I32Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I32Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector2Array_PyTypeObject = type;
        }
        api->I32Vector2_GetType = get_I32Vector2_type;
        api->I32Vector2Array_GetType = get_I32Vector2Array_type;
        api->I32Vector2_Create = create_I32Vector2;
        api->I32Vector2Array_Create = create_I32Vector2Array;
        api->I32Vector2_GetValuePointer = get_I32Vector2_value_ptr;
        api->I32Vector2Array_GetValuePointer = get_I32Vector2Array_value_ptr;
        api->I32Vector2Array_GetLength = get_I32Vector2Array_length;

        {
            PyTypeObject *type = define_U32Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U32Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector2Array_PyTypeObject = type;
        }
        api->U32Vector2_GetType = get_U32Vector2_type;
        api->U32Vector2Array_GetType = get_U32Vector2Array_type;
        api->U32Vector2_Create = create_U32Vector2;
        api->U32Vector2Array_Create = create_U32Vector2Array;
        api->U32Vector2_GetValuePointer = get_U32Vector2_value_ptr;
        api->U32Vector2Array_GetValuePointer = get_U32Vector2Array_value_ptr;
        api->U32Vector2Array_GetLength = get_U32Vector2Array_length;

        {
            PyTypeObject *type = define_IVector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_IVector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector2Array_PyTypeObject = type;
        }
        api->IVector2_GetType = get_IVector2_type;
        api->IVector2Array_GetType = get_IVector2Array_type;
        api->IVector2_Create = create_IVector2;
        api->IVector2Array_Create = create_IVector2Array;
        api->IVector2_GetValuePointer = get_IVector2_value_ptr;
        api->IVector2Array_GetValuePointer = get_IVector2Array_value_ptr;
        api->IVector2Array_GetLength = get_IVector2Array_length;

        {
            PyTypeObject *type = define_UVector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_UVector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector2Array_PyTypeObject = type;
        }
        api->UVector2_GetType = get_UVector2_type;
        api->UVector2Array_GetType = get_UVector2Array_type;
        api->UVector2_Create = create_UVector2;
        api->UVector2Array_Create = create_UVector2Array;
        api->UVector2_GetValuePointer = get_UVector2_value_ptr;
        api->UVector2Array_GetValuePointer = get_UVector2Array_value_ptr;
        api->UVector2Array_GetLength = get_UVector2Array_length;

        {
            PyTypeObject *type = define_I64Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I64Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector2Array_PyTypeObject = type;
        }
        api->I64Vector2_GetType = get_I64Vector2_type;
        api->I64Vector2Array_GetType = get_I64Vector2Array_type;
        api->I64Vector2_Create = create_I64Vector2;
        api->I64Vector2Array_Create = create_I64Vector2Array;
        api->I64Vector2_GetValuePointer = get_I64Vector2_value_ptr;
        api->I64Vector2Array_GetValuePointer = get_I64Vector2Array_value_ptr;
        api->I64Vector2Array_GetLength = get_I64Vector2Array_length;

        {
            PyTypeObject *type = define_U64Vector2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U64Vector2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector2Array_PyTypeObject = type;
        }
        api->U64Vector2_GetType = get_U64Vector2_type;
        api->U64Vector2Array_GetType = get_U64Vector2Array_type;
        api->U64Vector2_Create = create_U64Vector2;
        api->U64Vector2Array_Create = create_U64Vector2Array;
        api->U64Vector2_GetValuePointer = get_U64Vector2_value_ptr;
        api->U64Vector2Array_GetValuePointer = get_U64Vector2Array_value_ptr;
        api->U64Vector2Array_GetLength = get_U64Vector2Array_length;

        {
            PyTypeObject *type = define_BVector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_BVector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector3Array_PyTypeObject = type;
        }
        api->BVector3_GetType = get_BVector3_type;
        api->BVector3Array_GetType = get_BVector3Array_type;
        api->BVector3_Create = create_BVector3;
        api->BVector3Array_Create = create_BVector3Array;
        api->BVector3_GetValuePointer = get_BVector3_value_ptr;
        api->BVector3Array_GetValuePointer = get_BVector3Array_value_ptr;
        api->BVector3Array_GetLength = get_BVector3Array_length;

        {
            PyTypeObject *type = define_DVector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DVector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector3Array_PyTypeObject = type;
        }
        api->DVector3_GetType = get_DVector3_type;
        api->DVector3Array_GetType = get_DVector3Array_type;
        api->DVector3_Create = create_DVector3;
        api->DVector3Array_Create = create_DVector3Array;
        api->DVector3_GetValuePointer = get_DVector3_value_ptr;
        api->DVector3Array_GetValuePointer = get_DVector3Array_value_ptr;
        api->DVector3Array_GetLength = get_DVector3Array_length;

        {
            PyTypeObject *type = define_FVector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FVector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector3Array_PyTypeObject = type;
        }
        api->FVector3_GetType = get_FVector3_type;
        api->FVector3Array_GetType = get_FVector3Array_type;
        api->FVector3_Create = create_FVector3;
        api->FVector3Array_Create = create_FVector3Array;
        api->FVector3_GetValuePointer = get_FVector3_value_ptr;
        api->FVector3Array_GetValuePointer = get_FVector3Array_value_ptr;
        api->FVector3Array_GetLength = get_FVector3Array_length;

        {
            PyTypeObject *type = define_I8Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I8Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector3Array_PyTypeObject = type;
        }
        api->I8Vector3_GetType = get_I8Vector3_type;
        api->I8Vector3Array_GetType = get_I8Vector3Array_type;
        api->I8Vector3_Create = create_I8Vector3;
        api->I8Vector3Array_Create = create_I8Vector3Array;
        api->I8Vector3_GetValuePointer = get_I8Vector3_value_ptr;
        api->I8Vector3Array_GetValuePointer = get_I8Vector3Array_value_ptr;
        api->I8Vector3Array_GetLength = get_I8Vector3Array_length;

        {
            PyTypeObject *type = define_U8Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U8Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector3Array_PyTypeObject = type;
        }
        api->U8Vector3_GetType = get_U8Vector3_type;
        api->U8Vector3Array_GetType = get_U8Vector3Array_type;
        api->U8Vector3_Create = create_U8Vector3;
        api->U8Vector3Array_Create = create_U8Vector3Array;
        api->U8Vector3_GetValuePointer = get_U8Vector3_value_ptr;
        api->U8Vector3Array_GetValuePointer = get_U8Vector3Array_value_ptr;
        api->U8Vector3Array_GetLength = get_U8Vector3Array_length;

        {
            PyTypeObject *type = define_I16Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I16Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector3Array_PyTypeObject = type;
        }
        api->I16Vector3_GetType = get_I16Vector3_type;
        api->I16Vector3Array_GetType = get_I16Vector3Array_type;
        api->I16Vector3_Create = create_I16Vector3;
        api->I16Vector3Array_Create = create_I16Vector3Array;
        api->I16Vector3_GetValuePointer = get_I16Vector3_value_ptr;
        api->I16Vector3Array_GetValuePointer = get_I16Vector3Array_value_ptr;
        api->I16Vector3Array_GetLength = get_I16Vector3Array_length;

        {
            PyTypeObject *type = define_U16Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U16Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector3Array_PyTypeObject = type;
        }
        api->U16Vector3_GetType = get_U16Vector3_type;
        api->U16Vector3Array_GetType = get_U16Vector3Array_type;
        api->U16Vector3_Create = create_U16Vector3;
        api->U16Vector3Array_Create = create_U16Vector3Array;
        api->U16Vector3_GetValuePointer = get_U16Vector3_value_ptr;
        api->U16Vector3Array_GetValuePointer = get_U16Vector3Array_value_ptr;
        api->U16Vector3Array_GetLength = get_U16Vector3Array_length;

        {
            PyTypeObject *type = define_I32Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I32Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector3Array_PyTypeObject = type;
        }
        api->I32Vector3_GetType = get_I32Vector3_type;
        api->I32Vector3Array_GetType = get_I32Vector3Array_type;
        api->I32Vector3_Create = create_I32Vector3;
        api->I32Vector3Array_Create = create_I32Vector3Array;
        api->I32Vector3_GetValuePointer = get_I32Vector3_value_ptr;
        api->I32Vector3Array_GetValuePointer = get_I32Vector3Array_value_ptr;
        api->I32Vector3Array_GetLength = get_I32Vector3Array_length;

        {
            PyTypeObject *type = define_U32Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U32Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector3Array_PyTypeObject = type;
        }
        api->U32Vector3_GetType = get_U32Vector3_type;
        api->U32Vector3Array_GetType = get_U32Vector3Array_type;
        api->U32Vector3_Create = create_U32Vector3;
        api->U32Vector3Array_Create = create_U32Vector3Array;
        api->U32Vector3_GetValuePointer = get_U32Vector3_value_ptr;
        api->U32Vector3Array_GetValuePointer = get_U32Vector3Array_value_ptr;
        api->U32Vector3Array_GetLength = get_U32Vector3Array_length;

        {
            PyTypeObject *type = define_IVector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_IVector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector3Array_PyTypeObject = type;
        }
        api->IVector3_GetType = get_IVector3_type;
        api->IVector3Array_GetType = get_IVector3Array_type;
        api->IVector3_Create = create_IVector3;
        api->IVector3Array_Create = create_IVector3Array;
        api->IVector3_GetValuePointer = get_IVector3_value_ptr;
        api->IVector3Array_GetValuePointer = get_IVector3Array_value_ptr;
        api->IVector3Array_GetLength = get_IVector3Array_length;

        {
            PyTypeObject *type = define_UVector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_UVector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector3Array_PyTypeObject = type;
        }
        api->UVector3_GetType = get_UVector3_type;
        api->UVector3Array_GetType = get_UVector3Array_type;
        api->UVector3_Create = create_UVector3;
        api->UVector3Array_Create = create_UVector3Array;
        api->UVector3_GetValuePointer = get_UVector3_value_ptr;
        api->UVector3Array_GetValuePointer = get_UVector3Array_value_ptr;
        api->UVector3Array_GetLength = get_UVector3Array_length;

        {
            PyTypeObject *type = define_I64Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I64Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector3Array_PyTypeObject = type;
        }
        api->I64Vector3_GetType = get_I64Vector3_type;
        api->I64Vector3Array_GetType = get_I64Vector3Array_type;
        api->I64Vector3_Create = create_I64Vector3;
        api->I64Vector3Array_Create = create_I64Vector3Array;
        api->I64Vector3_GetValuePointer = get_I64Vector3_value_ptr;
        api->I64Vector3Array_GetValuePointer = get_I64Vector3Array_value_ptr;
        api->I64Vector3Array_GetLength = get_I64Vector3Array_length;

        {
            PyTypeObject *type = define_U64Vector3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U64Vector3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector3Array_PyTypeObject = type;
        }
        api->U64Vector3_GetType = get_U64Vector3_type;
        api->U64Vector3Array_GetType = get_U64Vector3Array_type;
        api->U64Vector3_Create = create_U64Vector3;
        api->U64Vector3Array_Create = create_U64Vector3Array;
        api->U64Vector3_GetValuePointer = get_U64Vector3_value_ptr;
        api->U64Vector3Array_GetValuePointer = get_U64Vector3Array_value_ptr;
        api->U64Vector3Array_GetLength = get_U64Vector3Array_length;

        {
            PyTypeObject *type = define_BVector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_BVector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BVector4Array_PyTypeObject = type;
        }
        api->BVector4_GetType = get_BVector4_type;
        api->BVector4Array_GetType = get_BVector4Array_type;
        api->BVector4_Create = create_BVector4;
        api->BVector4Array_Create = create_BVector4Array;
        api->BVector4_GetValuePointer = get_BVector4_value_ptr;
        api->BVector4Array_GetValuePointer = get_BVector4Array_value_ptr;
        api->BVector4Array_GetLength = get_BVector4Array_length;

        {
            PyTypeObject *type = define_DVector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DVector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DVector4Array_PyTypeObject = type;
        }
        api->DVector4_GetType = get_DVector4_type;
        api->DVector4Array_GetType = get_DVector4Array_type;
        api->DVector4_Create = create_DVector4;
        api->DVector4Array_Create = create_DVector4Array;
        api->DVector4_GetValuePointer = get_DVector4_value_ptr;
        api->DVector4Array_GetValuePointer = get_DVector4Array_value_ptr;
        api->DVector4Array_GetLength = get_DVector4Array_length;

        {
            PyTypeObject *type = define_FVector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FVector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FVector4Array_PyTypeObject = type;
        }
        api->FVector4_GetType = get_FVector4_type;
        api->FVector4Array_GetType = get_FVector4Array_type;
        api->FVector4_Create = create_FVector4;
        api->FVector4Array_Create = create_FVector4Array;
        api->FVector4_GetValuePointer = get_FVector4_value_ptr;
        api->FVector4Array_GetValuePointer = get_FVector4Array_value_ptr;
        api->FVector4Array_GetLength = get_FVector4Array_length;

        {
            PyTypeObject *type = define_I8Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I8Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Vector4Array_PyTypeObject = type;
        }
        api->I8Vector4_GetType = get_I8Vector4_type;
        api->I8Vector4Array_GetType = get_I8Vector4Array_type;
        api->I8Vector4_Create = create_I8Vector4;
        api->I8Vector4Array_Create = create_I8Vector4Array;
        api->I8Vector4_GetValuePointer = get_I8Vector4_value_ptr;
        api->I8Vector4Array_GetValuePointer = get_I8Vector4Array_value_ptr;
        api->I8Vector4Array_GetLength = get_I8Vector4Array_length;

        {
            PyTypeObject *type = define_U8Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U8Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Vector4Array_PyTypeObject = type;
        }
        api->U8Vector4_GetType = get_U8Vector4_type;
        api->U8Vector4Array_GetType = get_U8Vector4Array_type;
        api->U8Vector4_Create = create_U8Vector4;
        api->U8Vector4Array_Create = create_U8Vector4Array;
        api->U8Vector4_GetValuePointer = get_U8Vector4_value_ptr;
        api->U8Vector4Array_GetValuePointer = get_U8Vector4Array_value_ptr;
        api->U8Vector4Array_GetLength = get_U8Vector4Array_length;

        {
            PyTypeObject *type = define_I16Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I16Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Vector4Array_PyTypeObject = type;
        }
        api->I16Vector4_GetType = get_I16Vector4_type;
        api->I16Vector4Array_GetType = get_I16Vector4Array_type;
        api->I16Vector4_Create = create_I16Vector4;
        api->I16Vector4Array_Create = create_I16Vector4Array;
        api->I16Vector4_GetValuePointer = get_I16Vector4_value_ptr;
        api->I16Vector4Array_GetValuePointer = get_I16Vector4Array_value_ptr;
        api->I16Vector4Array_GetLength = get_I16Vector4Array_length;

        {
            PyTypeObject *type = define_U16Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U16Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Vector4Array_PyTypeObject = type;
        }
        api->U16Vector4_GetType = get_U16Vector4_type;
        api->U16Vector4Array_GetType = get_U16Vector4Array_type;
        api->U16Vector4_Create = create_U16Vector4;
        api->U16Vector4Array_Create = create_U16Vector4Array;
        api->U16Vector4_GetValuePointer = get_U16Vector4_value_ptr;
        api->U16Vector4Array_GetValuePointer = get_U16Vector4Array_value_ptr;
        api->U16Vector4Array_GetLength = get_U16Vector4Array_length;

        {
            PyTypeObject *type = define_I32Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I32Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Vector4Array_PyTypeObject = type;
        }
        api->I32Vector4_GetType = get_I32Vector4_type;
        api->I32Vector4Array_GetType = get_I32Vector4Array_type;
        api->I32Vector4_Create = create_I32Vector4;
        api->I32Vector4Array_Create = create_I32Vector4Array;
        api->I32Vector4_GetValuePointer = get_I32Vector4_value_ptr;
        api->I32Vector4Array_GetValuePointer = get_I32Vector4Array_value_ptr;
        api->I32Vector4Array_GetLength = get_I32Vector4Array_length;

        {
            PyTypeObject *type = define_U32Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U32Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Vector4Array_PyTypeObject = type;
        }
        api->U32Vector4_GetType = get_U32Vector4_type;
        api->U32Vector4Array_GetType = get_U32Vector4Array_type;
        api->U32Vector4_Create = create_U32Vector4;
        api->U32Vector4Array_Create = create_U32Vector4Array;
        api->U32Vector4_GetValuePointer = get_U32Vector4_value_ptr;
        api->U32Vector4Array_GetValuePointer = get_U32Vector4Array_value_ptr;
        api->U32Vector4Array_GetLength = get_U32Vector4Array_length;

        {
            PyTypeObject *type = define_IVector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_IVector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IVector4Array_PyTypeObject = type;
        }
        api->IVector4_GetType = get_IVector4_type;
        api->IVector4Array_GetType = get_IVector4Array_type;
        api->IVector4_Create = create_IVector4;
        api->IVector4Array_Create = create_IVector4Array;
        api->IVector4_GetValuePointer = get_IVector4_value_ptr;
        api->IVector4Array_GetValuePointer = get_IVector4Array_value_ptr;
        api->IVector4Array_GetLength = get_IVector4Array_length;

        {
            PyTypeObject *type = define_UVector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_UVector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UVector4Array_PyTypeObject = type;
        }
        api->UVector4_GetType = get_UVector4_type;
        api->UVector4Array_GetType = get_UVector4Array_type;
        api->UVector4_Create = create_UVector4;
        api->UVector4Array_Create = create_UVector4Array;
        api->UVector4_GetValuePointer = get_UVector4_value_ptr;
        api->UVector4Array_GetValuePointer = get_UVector4Array_value_ptr;
        api->UVector4Array_GetLength = get_UVector4Array_length;

        {
            PyTypeObject *type = define_I64Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_I64Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Vector4Array_PyTypeObject = type;
        }
        api->I64Vector4_GetType = get_I64Vector4_type;
        api->I64Vector4Array_GetType = get_I64Vector4Array_type;
        api->I64Vector4_Create = create_I64Vector4;
        api->I64Vector4Array_Create = create_I64Vector4Array;
        api->I64Vector4_GetValuePointer = get_I64Vector4_value_ptr;
        api->I64Vector4Array_GetValuePointer = get_I64Vector4Array_value_ptr;
        api->I64Vector4Array_GetLength = get_I64Vector4Array_length;

        {
            PyTypeObject *type = define_U64Vector4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_U64Vector4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Vector4Array_PyTypeObject = type;
        }
        api->U64Vector4_GetType = get_U64Vector4_type;
        api->U64Vector4Array_GetType = get_U64Vector4Array_type;
        api->U64Vector4_Create = create_U64Vector4;
        api->U64Vector4Array_Create = create_U64Vector4Array;
        api->U64Vector4_GetValuePointer = get_U64Vector4_value_ptr;
        api->U64Vector4Array_GetValuePointer = get_U64Vector4Array_value_ptr;
        api->U64Vector4Array_GetLength = get_U64Vector4Array_length;


        {
            PyTypeObject *type = define_DMatrix2x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix2x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x2Array_PyTypeObject = type;
        }
        api->DMatrix2x2_GetType = get_DMatrix2x2_type;
        api->DMatrix2x2Array_GetType = get_DMatrix2x2Array_type;
        api->DMatrix2x2_Create = create_DMatrix2x2;
        api->DMatrix2x2Array_Create = create_DMatrix2x2Array;
        api->DMatrix2x2_GetValuePointer = get_DMatrix2x2_value_ptr;
        api->DMatrix2x2Array_GetValuePointer = get_DMatrix2x2Array_value_ptr;
        api->DMatrix2x2Array_GetLength = get_DMatrix2x2Array_length;

        {
            PyTypeObject *type = define_FMatrix2x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix2x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x2Array_PyTypeObject = type;
        }
        api->FMatrix2x2_GetType = get_FMatrix2x2_type;
        api->FMatrix2x2Array_GetType = get_FMatrix2x2Array_type;
        api->FMatrix2x2_Create = create_FMatrix2x2;
        api->FMatrix2x2Array_Create = create_FMatrix2x2Array;
        api->FMatrix2x2_GetValuePointer = get_FMatrix2x2_value_ptr;
        api->FMatrix2x2Array_GetValuePointer = get_FMatrix2x2Array_value_ptr;
        api->FMatrix2x2Array_GetLength = get_FMatrix2x2Array_length;

        {
            PyTypeObject *type = define_DMatrix2x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix2x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x3Array_PyTypeObject = type;
        }
        api->DMatrix2x3_GetType = get_DMatrix2x3_type;
        api->DMatrix2x3Array_GetType = get_DMatrix2x3Array_type;
        api->DMatrix2x3_Create = create_DMatrix2x3;
        api->DMatrix2x3Array_Create = create_DMatrix2x3Array;
        api->DMatrix2x3_GetValuePointer = get_DMatrix2x3_value_ptr;
        api->DMatrix2x3Array_GetValuePointer = get_DMatrix2x3Array_value_ptr;
        api->DMatrix2x3Array_GetLength = get_DMatrix2x3Array_length;

        {
            PyTypeObject *type = define_FMatrix2x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix2x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x3Array_PyTypeObject = type;
        }
        api->FMatrix2x3_GetType = get_FMatrix2x3_type;
        api->FMatrix2x3Array_GetType = get_FMatrix2x3Array_type;
        api->FMatrix2x3_Create = create_FMatrix2x3;
        api->FMatrix2x3Array_Create = create_FMatrix2x3Array;
        api->FMatrix2x3_GetValuePointer = get_FMatrix2x3_value_ptr;
        api->FMatrix2x3Array_GetValuePointer = get_FMatrix2x3Array_value_ptr;
        api->FMatrix2x3Array_GetLength = get_FMatrix2x3Array_length;

        {
            PyTypeObject *type = define_DMatrix2x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix2x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix2x4Array_PyTypeObject = type;
        }
        api->DMatrix2x4_GetType = get_DMatrix2x4_type;
        api->DMatrix2x4Array_GetType = get_DMatrix2x4Array_type;
        api->DMatrix2x4_Create = create_DMatrix2x4;
        api->DMatrix2x4Array_Create = create_DMatrix2x4Array;
        api->DMatrix2x4_GetValuePointer = get_DMatrix2x4_value_ptr;
        api->DMatrix2x4Array_GetValuePointer = get_DMatrix2x4Array_value_ptr;
        api->DMatrix2x4Array_GetLength = get_DMatrix2x4Array_length;

        {
            PyTypeObject *type = define_FMatrix2x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix2x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix2x4Array_PyTypeObject = type;
        }
        api->FMatrix2x4_GetType = get_FMatrix2x4_type;
        api->FMatrix2x4Array_GetType = get_FMatrix2x4Array_type;
        api->FMatrix2x4_Create = create_FMatrix2x4;
        api->FMatrix2x4Array_Create = create_FMatrix2x4Array;
        api->FMatrix2x4_GetValuePointer = get_FMatrix2x4_value_ptr;
        api->FMatrix2x4Array_GetValuePointer = get_FMatrix2x4Array_value_ptr;
        api->FMatrix2x4Array_GetLength = get_FMatrix2x4Array_length;

        {
            PyTypeObject *type = define_DMatrix3x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix3x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x2Array_PyTypeObject = type;
        }
        api->DMatrix3x2_GetType = get_DMatrix3x2_type;
        api->DMatrix3x2Array_GetType = get_DMatrix3x2Array_type;
        api->DMatrix3x2_Create = create_DMatrix3x2;
        api->DMatrix3x2Array_Create = create_DMatrix3x2Array;
        api->DMatrix3x2_GetValuePointer = get_DMatrix3x2_value_ptr;
        api->DMatrix3x2Array_GetValuePointer = get_DMatrix3x2Array_value_ptr;
        api->DMatrix3x2Array_GetLength = get_DMatrix3x2Array_length;

        {
            PyTypeObject *type = define_FMatrix3x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix3x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x2Array_PyTypeObject = type;
        }
        api->FMatrix3x2_GetType = get_FMatrix3x2_type;
        api->FMatrix3x2Array_GetType = get_FMatrix3x2Array_type;
        api->FMatrix3x2_Create = create_FMatrix3x2;
        api->FMatrix3x2Array_Create = create_FMatrix3x2Array;
        api->FMatrix3x2_GetValuePointer = get_FMatrix3x2_value_ptr;
        api->FMatrix3x2Array_GetValuePointer = get_FMatrix3x2Array_value_ptr;
        api->FMatrix3x2Array_GetLength = get_FMatrix3x2Array_length;

        {
            PyTypeObject *type = define_DMatrix3x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix3x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x3Array_PyTypeObject = type;
        }
        api->DMatrix3x3_GetType = get_DMatrix3x3_type;
        api->DMatrix3x3Array_GetType = get_DMatrix3x3Array_type;
        api->DMatrix3x3_Create = create_DMatrix3x3;
        api->DMatrix3x3Array_Create = create_DMatrix3x3Array;
        api->DMatrix3x3_GetValuePointer = get_DMatrix3x3_value_ptr;
        api->DMatrix3x3Array_GetValuePointer = get_DMatrix3x3Array_value_ptr;
        api->DMatrix3x3Array_GetLength = get_DMatrix3x3Array_length;

        {
            PyTypeObject *type = define_FMatrix3x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix3x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x3Array_PyTypeObject = type;
        }
        api->FMatrix3x3_GetType = get_FMatrix3x3_type;
        api->FMatrix3x3Array_GetType = get_FMatrix3x3Array_type;
        api->FMatrix3x3_Create = create_FMatrix3x3;
        api->FMatrix3x3Array_Create = create_FMatrix3x3Array;
        api->FMatrix3x3_GetValuePointer = get_FMatrix3x3_value_ptr;
        api->FMatrix3x3Array_GetValuePointer = get_FMatrix3x3Array_value_ptr;
        api->FMatrix3x3Array_GetLength = get_FMatrix3x3Array_length;

        {
            PyTypeObject *type = define_DMatrix3x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix3x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix3x4Array_PyTypeObject = type;
        }
        api->DMatrix3x4_GetType = get_DMatrix3x4_type;
        api->DMatrix3x4Array_GetType = get_DMatrix3x4Array_type;
        api->DMatrix3x4_Create = create_DMatrix3x4;
        api->DMatrix3x4Array_Create = create_DMatrix3x4Array;
        api->DMatrix3x4_GetValuePointer = get_DMatrix3x4_value_ptr;
        api->DMatrix3x4Array_GetValuePointer = get_DMatrix3x4Array_value_ptr;
        api->DMatrix3x4Array_GetLength = get_DMatrix3x4Array_length;

        {
            PyTypeObject *type = define_FMatrix3x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix3x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix3x4Array_PyTypeObject = type;
        }
        api->FMatrix3x4_GetType = get_FMatrix3x4_type;
        api->FMatrix3x4Array_GetType = get_FMatrix3x4Array_type;
        api->FMatrix3x4_Create = create_FMatrix3x4;
        api->FMatrix3x4Array_Create = create_FMatrix3x4Array;
        api->FMatrix3x4_GetValuePointer = get_FMatrix3x4_value_ptr;
        api->FMatrix3x4Array_GetValuePointer = get_FMatrix3x4Array_value_ptr;
        api->FMatrix3x4Array_GetLength = get_FMatrix3x4Array_length;

        {
            PyTypeObject *type = define_DMatrix4x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix4x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x2Array_PyTypeObject = type;
        }
        api->DMatrix4x2_GetType = get_DMatrix4x2_type;
        api->DMatrix4x2Array_GetType = get_DMatrix4x2Array_type;
        api->DMatrix4x2_Create = create_DMatrix4x2;
        api->DMatrix4x2Array_Create = create_DMatrix4x2Array;
        api->DMatrix4x2_GetValuePointer = get_DMatrix4x2_value_ptr;
        api->DMatrix4x2Array_GetValuePointer = get_DMatrix4x2Array_value_ptr;
        api->DMatrix4x2Array_GetLength = get_DMatrix4x2Array_length;

        {
            PyTypeObject *type = define_FMatrix4x2_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x2_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix4x2Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x2Array_PyTypeObject = type;
        }
        api->FMatrix4x2_GetType = get_FMatrix4x2_type;
        api->FMatrix4x2Array_GetType = get_FMatrix4x2Array_type;
        api->FMatrix4x2_Create = create_FMatrix4x2;
        api->FMatrix4x2Array_Create = create_FMatrix4x2Array;
        api->FMatrix4x2_GetValuePointer = get_FMatrix4x2_value_ptr;
        api->FMatrix4x2Array_GetValuePointer = get_FMatrix4x2Array_value_ptr;
        api->FMatrix4x2Array_GetLength = get_FMatrix4x2Array_length;

        {
            PyTypeObject *type = define_DMatrix4x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix4x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x3Array_PyTypeObject = type;
        }
        api->DMatrix4x3_GetType = get_DMatrix4x3_type;
        api->DMatrix4x3Array_GetType = get_DMatrix4x3Array_type;
        api->DMatrix4x3_Create = create_DMatrix4x3;
        api->DMatrix4x3Array_Create = create_DMatrix4x3Array;
        api->DMatrix4x3_GetValuePointer = get_DMatrix4x3_value_ptr;
        api->DMatrix4x3Array_GetValuePointer = get_DMatrix4x3Array_value_ptr;
        api->DMatrix4x3Array_GetLength = get_DMatrix4x3Array_length;

        {
            PyTypeObject *type = define_FMatrix4x3_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x3_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix4x3Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x3Array_PyTypeObject = type;
        }
        api->FMatrix4x3_GetType = get_FMatrix4x3_type;
        api->FMatrix4x3Array_GetType = get_FMatrix4x3Array_type;
        api->FMatrix4x3_Create = create_FMatrix4x3;
        api->FMatrix4x3Array_Create = create_FMatrix4x3Array;
        api->FMatrix4x3_GetValuePointer = get_FMatrix4x3_value_ptr;
        api->FMatrix4x3Array_GetValuePointer = get_FMatrix4x3Array_value_ptr;
        api->FMatrix4x3Array_GetLength = get_FMatrix4x3Array_length;

        {
            PyTypeObject *type = define_DMatrix4x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DMatrix4x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DMatrix4x4Array_PyTypeObject = type;
        }
        api->DMatrix4x4_GetType = get_DMatrix4x4_type;
        api->DMatrix4x4Array_GetType = get_DMatrix4x4Array_type;
        api->DMatrix4x4_Create = create_DMatrix4x4;
        api->DMatrix4x4Array_Create = create_DMatrix4x4Array;
        api->DMatrix4x4_GetValuePointer = get_DMatrix4x4_value_ptr;
        api->DMatrix4x4Array_GetValuePointer = get_DMatrix4x4Array_value_ptr;
        api->DMatrix4x4Array_GetLength = get_DMatrix4x4Array_length;

        {
            PyTypeObject *type = define_FMatrix4x4_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x4_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FMatrix4x4Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FMatrix4x4Array_PyTypeObject = type;
        }
        api->FMatrix4x4_GetType = get_FMatrix4x4_type;
        api->FMatrix4x4Array_GetType = get_FMatrix4x4Array_type;
        api->FMatrix4x4_Create = create_FMatrix4x4;
        api->FMatrix4x4Array_Create = create_FMatrix4x4Array;
        api->FMatrix4x4_GetValuePointer = get_FMatrix4x4_value_ptr;
        api->FMatrix4x4Array_GetValuePointer = get_FMatrix4x4Array_value_ptr;
        api->FMatrix4x4Array_GetLength = get_FMatrix4x4Array_length;


        {
            PyTypeObject *type = define_DQuaternion_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DQuaternion_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_DQuaternionArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DQuaternionArray_PyTypeObject = type;
        }
        api->DQuaternion_GetType = get_DQuaternion_type;
        api->DQuaternionArray_GetType = get_DQuaternionArray_type;
        api->DQuaternion_Create = create_DQuaternion;
        api->DQuaternionArray_Create = create_DQuaternionArray;
        api->DQuaternion_GetValuePointer = get_DQuaternion_value_ptr;
        api->DQuaternionArray_GetValuePointer = get_DQuaternionArray_value_ptr;
        api->DQuaternionArray_GetLength = get_DQuaternionArray_length;

        {
            PyTypeObject *type = define_FQuaternion_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FQuaternion_PyTypeObject = type;
        }
        {
            PyTypeObject *type = define_FQuaternionArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FQuaternionArray_PyTypeObject = type;
        }
        api->FQuaternion_GetType = get_FQuaternion_type;
        api->FQuaternionArray_GetType = get_FQuaternionArray_type;
        api->FQuaternion_Create = create_FQuaternion;
        api->FQuaternionArray_Create = create_FQuaternionArray;
        api->FQuaternion_GetValuePointer = get_FQuaternion_value_ptr;
        api->FQuaternionArray_GetValuePointer = get_FQuaternionArray_value_ptr;
        api->FQuaternionArray_GetLength = get_FQuaternionArray_length;


        {
            PyTypeObject *type = define_BArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->BArray_PyTypeObject = type;
        }
        api->BArray_GetType = get_BArray_type;
        api->BArray_Create = create_BArray;
        api->BArray_GetValuePointer = get_BArray_value_ptr;
        api->BArray_GetLength = get_BArray_length;

        {
            PyTypeObject *type = define_DArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->DArray_PyTypeObject = type;
        }
        api->DArray_GetType = get_DArray_type;
        api->DArray_Create = create_DArray;
        api->DArray_GetValuePointer = get_DArray_value_ptr;
        api->DArray_GetLength = get_DArray_length;

        {
            PyTypeObject *type = define_FArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->FArray_PyTypeObject = type;
        }
        api->FArray_GetType = get_FArray_type;
        api->FArray_Create = create_FArray;
        api->FArray_GetValuePointer = get_FArray_value_ptr;
        api->FArray_GetLength = get_FArray_length;

        {
            PyTypeObject *type = define_I8Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I8Array_PyTypeObject = type;
        }
        api->I8Array_GetType = get_I8Array_type;
        api->I8Array_Create = create_I8Array;
        api->I8Array_GetValuePointer = get_I8Array_value_ptr;
        api->I8Array_GetLength = get_I8Array_length;

        {
            PyTypeObject *type = define_U8Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U8Array_PyTypeObject = type;
        }
        api->U8Array_GetType = get_U8Array_type;
        api->U8Array_Create = create_U8Array;
        api->U8Array_GetValuePointer = get_U8Array_value_ptr;
        api->U8Array_GetLength = get_U8Array_length;

        {
            PyTypeObject *type = define_I16Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I16Array_PyTypeObject = type;
        }
        api->I16Array_GetType = get_I16Array_type;
        api->I16Array_Create = create_I16Array;
        api->I16Array_GetValuePointer = get_I16Array_value_ptr;
        api->I16Array_GetLength = get_I16Array_length;

        {
            PyTypeObject *type = define_U16Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U16Array_PyTypeObject = type;
        }
        api->U16Array_GetType = get_U16Array_type;
        api->U16Array_Create = create_U16Array;
        api->U16Array_GetValuePointer = get_U16Array_value_ptr;
        api->U16Array_GetLength = get_U16Array_length;

        {
            PyTypeObject *type = define_I32Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I32Array_PyTypeObject = type;
        }
        api->I32Array_GetType = get_I32Array_type;
        api->I32Array_Create = create_I32Array;
        api->I32Array_GetValuePointer = get_I32Array_value_ptr;
        api->I32Array_GetLength = get_I32Array_length;

        {
            PyTypeObject *type = define_U32Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U32Array_PyTypeObject = type;
        }
        api->U32Array_GetType = get_U32Array_type;
        api->U32Array_Create = create_U32Array;
        api->U32Array_GetValuePointer = get_U32Array_value_ptr;
        api->U32Array_GetLength = get_U32Array_length;

        {
            PyTypeObject *type = define_IArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->IArray_PyTypeObject = type;
        }
        api->IArray_GetType = get_IArray_type;
        api->IArray_Create = create_IArray;
        api->IArray_GetValuePointer = get_IArray_value_ptr;
        api->IArray_GetLength = get_IArray_length;

        {
            PyTypeObject *type = define_UArray_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->UArray_PyTypeObject = type;
        }
        api->UArray_GetType = get_UArray_type;
        api->UArray_Create = create_UArray;
        api->UArray_GetValuePointer = get_UArray_value_ptr;
        api->UArray_GetLength = get_UArray_length;

        {
            PyTypeObject *type = define_I64Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->I64Array_PyTypeObject = type;
        }
        api->I64Array_GetType = get_I64Array_type;
        api->I64Array_Create = create_I64Array;
        api->I64Array_GetValuePointer = get_I64Array_value_ptr;
        api->I64Array_GetLength = get_I64Array_length;

        {
            PyTypeObject *type = define_U64Array_type(module);
            if (!type){ goto error; }
            Py_INCREF(type);
            state->U64Array_PyTypeObject = type;
        }
        api->U64Array_GetType = get_U64Array_type;
        api->U64Array_Create = create_U64Array;
        api->U64Array_GetValuePointer = get_U64Array_value_ptr;
        api->U64Array_GetLength = get_U64Array_length;


    if (PyModule_AddObject(module, "_api", api_capsule) < 0){ goto error; }

    return module;
error:
    delete api;
    Py_DECREF(api_capsule);
    Py_CLEAR(module);
    return 0;
}


static PyObject *
get_module()
{
    PyObject *module = PyState_FindModule(&module_PyModuleDef);
    if (!module)
    {
        return PyErr_Format(PyExc_RuntimeError, "math module not ready");
    }
    return module;
}

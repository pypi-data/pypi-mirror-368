#pragma once
#include <Python.h>
#include "structmember.h"
#include "bc7enc.h"

PyObject *PyBC7CompressBlockParamsObject = nullptr;

typedef struct
{
    PyObject_HEAD
        bc7enc_compress_block_params params;
} PyBC7CompressBlockParams;

static void PyBC7CompressBlockParams_dealloc(PyBC7CompressBlockParams *self)
{
    PyObject_Del(self);
}

static int PyBC7CompressBlockParams_init(PyBC7CompressBlockParams *self, PyObject *args, PyObject *kwds)
{

    memset(&self->params, 0, sizeof(bc7enc_compress_block_params));
    bc7enc_compress_block_params_init(&self->params);
    return 0;
}

// MEMBER DEFINITIONS.............................................
static PyMemberDef PyBC7CompressBlockParams_members[] = {
    {"m_mode_mask", T_UINT, offsetof(PyBC7CompressBlockParams, params.m_mode_mask), 0, "Mode mask"},
    {"m_max_partitions", T_UINT, offsetof(PyBC7CompressBlockParams, params.m_max_partitions), 0, "Max partitions"},
    // {"m_weights", T_UINT, offsetof(PyBC7CompressBlockParams, params.m_weights), 0, "Weights"},
    {"m_uber_level", T_UINT, offsetof(PyBC7CompressBlockParams, params.m_uber_level), 0, "Uber level"},
    {"m_perceptual", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_perceptual), 0, "Perceptual"},
    {"m_try_least_squares", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_try_least_squares), 0, "Try least squares"},
    {"m_mode17_partition_estimation_filterbank", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_mode17_partition_estimation_filterbank), 0, "Mode 1/7 partition estimation filterbank"},
    {"m_force_alpha", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_force_alpha), 0, "Force alpha"},
    {"m_force_selectors", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_force_selectors), 0, "Force selectors"},
    // {"m_selectors", T_BYTE, offsetof(PyBC7CompressBlockParams, params.m_selectors), 0, "Selectors"},
    {"m_quant_mode6_endpoints", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_quant_mode6_endpoints), 0, "Quant mode 6 endpoints"},
    {"m_bias_mode1_pbits", T_BOOL, offsetof(PyBC7CompressBlockParams, params.m_bias_mode1_pbits), 0, "Bias mode 1 p-bits"},
    {"m_pbit1_weight", T_FLOAT, offsetof(PyBC7CompressBlockParams, params.m_pbit1_weight), 0, "p-bit 1 weight"},
    {"m_mode1_error_weight", T_FLOAT, offsetof(PyBC7CompressBlockParams, params.m_mode1_error_weight), 0, "Mode 1 error weight"},
    {"m_mode5_error_weight", T_FLOAT, offsetof(PyBC7CompressBlockParams, params.m_mode5_error_weight), 0, "Mode 5 error weight"},
    {"m_mode6_error_weight", T_FLOAT, offsetof(PyBC7CompressBlockParams, params.m_mode6_error_weight), 0, "Mode 6 error weight"},
    {"m_mode7_error_weight", T_FLOAT, offsetof(PyBC7CompressBlockParams, params.m_mode7_error_weight), 0, "Mode 7 error weight"},
    {NULL} /* Sentinel */
};

// GETTER/SETTER DEFINITIONS.............................................
// Getter for the weights attribute
static PyObject *PyBC7CompressBlockParams_get_weights(PyBC7CompressBlockParams *self, void *closure)
{
    PyObject *list = PyList_New(4);
    for (int i = 0; i < 4; i++)
    {
        PyList_SetItem(list, i, PyLong_FromUnsignedLong(self->params.m_weights[i]));
    }
    return list;
}

// Setter for the weights attribute
static int PyBC7CompressBlockParams_set_weights(PyBC7CompressBlockParams *self, PyObject *value, void *closure)
{
    if (!PyList_Check(value) || PyList_Size(value) != 4)
    {
        PyErr_SetString(PyExc_ValueError, "Weights must be a list of 4 unsigned integers.");
        return -1;
    }
    for (int i = 0; i < 4; i++)
    {
        PyObject *item = PyList_GetItem(value, i);
        if (!PyLong_Check(item))
        {
            PyErr_SetString(PyExc_ValueError, "Weights must be a list of unsigned integers.");
            return -1;
        }
        self->params.m_weights[i] = (uint32_t)PyLong_AsUnsignedLong(item);
    }
    return 0;
}

// Getter for the selectors attribute
static PyObject *PyBC7CompressBlockParams_get_selectors(PyBC7CompressBlockParams *self, void *closure)
{
    PyObject *list = PyList_New(16);
    for (int i = 0; i < 16; i++)
    {
        PyList_SetItem(list, i, PyLong_FromUnsignedLong(self->params.m_selectors[i]));
    }
    return list;
}

// Setter for the selectors attribute
static int PyBC7CompressBlockParams_set_selectors(PyBC7CompressBlockParams *self, PyObject *value, void *closure)
{
    if (!PyList_Check(value) || PyList_Size(value) != 16)
    {
        PyErr_SetString(PyExc_ValueError, "Selectors must be a list of 16 unsigned integers.");
        return -1;
    }
    for (int i = 0; i < 16; i++)
    {
        PyObject *item = PyList_GetItem(value, i);
        if (!PyLong_Check(item))
        {
            PyErr_SetString(PyExc_ValueError, "Selectors must be a list of unsigned integers.");
            return -1;
        }
        self->params.m_selectors[i] = (uint8_t)PyLong_AsUnsignedLong(item);
    }
    return 0;
}

static PyGetSetDef PyBC7CompressBlockParams_getseters[] = {
    {"m_weights", (getter)PyBC7CompressBlockParams_get_weights, (setter)PyBC7CompressBlockParams_set_weights,
     "Weights", NULL},
    {"m_selectors", (getter)PyBC7CompressBlockParams_get_selectors, (setter)PyBC7CompressBlockParams_set_selectors,
     "Selectors", NULL},
    {NULL} /* Sentinel */
};

// METHODS DEFINITIONS.............................................
// Function to initialize linear weights
static PyObject *PyBC7CompressBlockParams_init_linear_weights(PyBC7CompressBlockParams *self, PyObject *args)
{
    bc7enc_compress_block_params_init_linear_weights(&self->params);
    Py_RETURN_NONE;
}

// Function to initialize perceptual weights
static PyObject *PyBC7CompressBlockParams_init_perceptual_weights(PyBC7CompressBlockParams *self, PyObject *args)
{
    bc7enc_compress_block_params_init_perceptual_weights(&self->params);
    Py_RETURN_NONE;
}

static PyMethodDef PyBC7CompressBlockParams_methods[] = {
    {"init_linear_weights", (PyCFunction)PyBC7CompressBlockParams_init_linear_weights, METH_NOARGS,
     "Initialize with linear weights"},
    {"init_perceptual_weights", (PyCFunction)PyBC7CompressBlockParams_init_perceptual_weights, METH_NOARGS,
     "Initialize with perceptual weights"},
    {NULL} /* Sentinel */
};

// TYPE DEFINITION.............................................
static PyType_Slot PyBC7CompressBlockParams_slots[] = {
    {Py_tp_dealloc, (void *)PyBC7CompressBlockParams_dealloc},
    {Py_tp_doc, (void *)"BC7 Compress Block Params"},
    {Py_tp_init, (void *)PyBC7CompressBlockParams_init},
    {Py_tp_members, PyBC7CompressBlockParams_members},
    {Py_tp_getset, PyBC7CompressBlockParams_getseters},
    {Py_tp_methods, PyBC7CompressBlockParams_methods},
    {Py_tp_new, (void *)PyType_GenericNew},
    {0, NULL},
};

static PyType_Spec PyBC7CompressBlockParamsType_Spec = {
    "etcpak.BC7CompressBlockParams",          // const char* name;
    sizeof(PyBC7CompressBlockParams),         // int basicsize;
    0,                                        // int itemsize;
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, // unsigned int flags;
    PyBC7CompressBlockParams_slots            // PyType_Slot *slots;
};

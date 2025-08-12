#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>

static void getCurvePoint(double x1, double y1, double x2, double y2,
                          double x3, double y3, double x4, double y4,
                          double t, double *out_x, double *out_y) {
    double l_t = 1.0 - t;
    double powA = l_t * l_t;
    double powB = t * t;
    double kA = l_t * powA;
    double kB = 3.0 * t * powA;
    double kC = 3.0 * l_t * powB;
    double kD = t * powB;
    *out_x = kA * x1 + kB * x2 + kC * x3 + kD * x4;
    *out_y = kA * y1 + kB * y2 + kC * y3 + kD * y4;
}

static int jsRound(double x) {
    double tx = x * 10000;
    return (tx >= 0.0) ? (int)floor(tx + 0.5) : (int)ceil(tx - 0.5);
}

static PyObject* py_getCurves(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *curve_obj;
    int count;
    int mode = 1;
    static char *kwlist[] = {"curve", "count", "mode", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi|p", kwlist, &curve_obj, &count, &mode)) {
        return NULL;
    }

    Py_ssize_t curve_len = PySequence_Length(curve_obj);
    double *curve = malloc(sizeof(double) * curve_len);
    if (!curve) return PyErr_NoMemory();
    for (Py_ssize_t i = 0; i < curve_len; i++) {
        PyObject *item = PySequence_GetItem(curve_obj, i);
        curve[i] = PyFloat_AsDouble(item);
        Py_DECREF(item);
    }

    PyObject *result = PyList_New(count);
    int step = -2;
    for (int i = 0; i < count; i++) {
        double t = (i + 1.0) / (count + 1.0);
        while (step + 6 < curve_len && curve[step + 6] < t) {
            step += 6;
        }

        double x1, y1, x2, y2, x3, y3, x4, y4;
        double lower, higher;
        if (0 <= step && step < curve_len - 6) {
            x1 = curve[step];
            y1 = curve[step + 1];
            x2 = curve[step + 2];
            y2 = curve[step + 3];
            x3 = curve[step + 4];
            y3 = curve[step + 5];
            x4 = curve[step + 6];
            y4 = curve[step + 7];
            lower = 0.0; higher = 1.0;
        } else {
            x1 = 0.0; y1 = 0.0;
            x2 = curve[step + 2]; y2 = curve[step + 3];
            x3 = curve[step + 4]; y3 = curve[step + 5];
            x4 = 1.0; y4 = 1.0;
            lower = 0.0; higher = 1.0;
        }
        double cy_last = 0.0;
        while (higher - lower > 0.0001) {
            double percentage = (lower + higher) / 2.0;
            double cx, cy;
            getCurvePoint(x1, y1, x2, y2, x3, y3, x4, y4, percentage, &cx, &cy);
            cy_last = cy;
            if (t > cx) {
                lower = percentage;
            } else {
                higher = percentage;
            }
        }

        double y_val = cy_last;

        if (mode) {
            PyList_SET_ITEM(result, i, PyFloat_FromDouble(y_val));
        } else {
            PyList_SET_ITEM(result, i, PyLong_FromLong(jsRound(y_val)));
        }
    }

    free(curve);
    return result;
}

static PyMethodDef PY2dMathMethods[] = {
    {"getCurves", (PyCFunction)py_getCurves, METH_VARARGS | METH_KEYWORDS, "Calculate Bezier curve values"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef py2dmathmodule = {
    PyModuleDef_HEAD_INIT,
    "py2dmath",
    NULL,
    -1,
    PY2dMathMethods
};

PyMODINIT_FUNC PyInit_py2dmath(void) {
    return PyModule_Create(&py2dmathmodule);
}

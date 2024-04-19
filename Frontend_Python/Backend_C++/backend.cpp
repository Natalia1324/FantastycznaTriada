/**
*@package FantastycznaTriada
*Dokumentacja dla modułu Backend_C++/Backend.cpp.
*
*Zawiera definicje modulu PyBind11
*/

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include"backend.h"

namespace py = pybind11;


PYBIND11_MODULE(backend, m) {
/**
*
Funkcja definiuje moduł "backend" zawierający powiązania między C++ a Pythonem, 
w tym klasę "Poziom" z metodą "read_csv_to_numpy" i właściwościami tylko do odczytu, 
takimi jak "tile_size", "vertical_tile_number", "screen_height" i "screen_width".
*/
    py::class_<Poziom>(m, "Poziom")
        .def(py::init<>())
        .def("read_csv_to_numpy", &Poziom::read_csv_to_numpy, py::arg("filename"), py::arg("delimiter") = ',')
        .def_readonly("tile_size", &Poziom::tile_size)
        .def_readonly("vertical_tile_number", &Poziom::vertical_tile_number)
        .def_readonly("screen_height", &Poziom::screen_height)
        .def_readonly("screen_width", &Poziom::screen_width);


#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
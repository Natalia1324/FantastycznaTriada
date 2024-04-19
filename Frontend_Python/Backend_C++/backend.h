/**
*@package FantastycznaTriada
*Dokumentacja dla modułu Backend_C++/Backend.h.
*
*Zawiera klase Poziom.
*/

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <thread>
#include <future>

namespace py = pybind11;

class Poziom {
public:

    /**
    * Konstruktor klasy Poziom
    */
    Poziom(){}
    /**
    * Destruktor klasy Poziom
    */
    ~Poziom(){}

    /**
    * vertical_tile_number - ilosc plytek graficznych w pionie
    */
    const int vertical_tile_number = 11;
    /**
    * tile_size - rozmiar plytki (tutaj sa one 64x64 piksele)
    */
    const int tile_size = 64;
    /**
    * screen_height - wysokosc ekranu
    */
    const int screen_height = vertical_tile_number * tile_size;
    /**
    * screen_width - szerokosc ekranu
    */
    const int screen_width = 1200;

    py::array_t<int> read_csv_to_numpy(const std::string& filename, char delimiter = ',') {
        /**
         * Funkcja odczytuje plik CSV o podanej nazwie i zwraca dane w postaci tablicy NumPy 
         * w formacie int. Funkcja wczytuje plik wiersz po wierszu, 
         * dzieląc każdy wiersz na komórki za pomocą określonego separatora. 
         * Następnie dane są konwertowane na liczby całkowite i zapisywane w 
         * wektorze dwuwymiarowym. Na podstawie rozmiaru danych, 
         * tworzona jest tablica NumPy, a następnie dane są przepisywane do tej tablicy. 
         * Parametry:
         * - filename - sciezka do pliku
         * - delimiter - separator (domyslnie ',')
         * 
         * Zwraca:
         * - result - kontener NumPy zawierajacy uklad z pliku CSV
         */
        std::vector<std::vector<int>> data;
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Błąd podczas otwierania pliku: " + filename);
        }

        std::string line;
        while (std::getline(file, line)) {
            std::vector<int> row;
            std::stringstream ss(line);
            std::string cell;
            while (std::getline(ss, cell, delimiter)) {
                row.push_back(std::stoi(cell));
            }
            data.push_back(row);
        }

        size_t rows = data.size();
        size_t cols = (rows > 0) ? data[0].size() : 0;

        auto result = py::array_t<int>({ rows, cols });
        auto result_buffer = result.request();
        int* result_ptr = static_cast<int*>(result_buffer.ptr);

        for (size_t i = 0; i < rows; i++) {
            for (size_t j = 0; j < cols; j++) {
                result_ptr[i * cols + j] = data[i][j];
            }
        }

        return result;
    }
};


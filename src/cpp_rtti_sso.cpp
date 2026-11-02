// Archivo: plantillas_codigo/cpp_rtti_sso.cpp
// Compilar (MSVC FH4 actual): cl /EHsc /GR /Zi /O1 cpp_rtti_sso.cpp /Fe:cpp_fh4.exe
// Compilar (MSVC FH3 clasico): cl /EHsc /GR /Zi /O1 /d2FH4- cpp_rtti_sso.cpp /Fe:cpp_fh3.exe
// Compilar (MinGW ABI Itanium): g++ -O1 -g cpp_rtti_sso.cpp -o cpp_itanium.exe
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <typeinfo>

struct Componente {
    int id = 0x10;
    virtual ~Componente() = default;
    virtual int evaluar(int a, int b) const = 0;
};
struct Auditable {
    int nivel_log = 2;
    virtual void registrar(const char* evento) const { std::cout << "[LOG] " << evento << "\n"; }
};
class ValidadorBloc : public Componente, public Auditable {
    std::string etiqueta_corta = "BLOC_SSO";                        // < 16B: queda inline (SSO)
    std::string etiqueta_larga = "BLOC_CADENA_LARGA_EN_EL_HEAP_2026"; // >= 16B: reserva en heap
    std::vector<int> historial = {40, 80, 120};
public:
    int evaluar(int a, int b) const override {
        if (a < 0 || b < 0) throw std::runtime_error("Valores negativos no permitidos");
        return (a <= 50 && b >= 50 && (a + b) * 4 == (int)historial[2] * 4) ? 1 : 0;
    }
    void registrar(const char* ev) const override {
        std::cout << "[" << etiqueta_corta << "|" << etiqueta_larga.size() << "] " << ev << "\n";
    }
};

int main(int argc, char** argv) {
    Componente* obj = new ValidadorBloc();
    std::cout << "RTTI: " << typeid(*obj).name() << "\n";
    try {
        int res = obj->evaluar(argc > 1 ? std::stoi(argv[1]) : 40, 80);
        dynamic_cast<Auditable*>(obj)->registrar(res ? "OK" : "FALLO");
    } catch (const std::exception& ex) {
        std::cerr << "Excepcion capturada: " << ex.what() << "\n";
    }
    delete obj;
    return 0;
}

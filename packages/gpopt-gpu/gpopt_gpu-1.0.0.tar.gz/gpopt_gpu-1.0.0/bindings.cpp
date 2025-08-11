#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "gpopt/config.h"
#include "core/Evolution.h"

namespace py = pybind11;

// wrapper class to be exposed to Python
class GpoptRunner {
public:
    GpoptRunner(GpoptConfig config) : config_(config), evolution_(config) {}

    void initialize(const std::vector<float>& X, const std::vector<float>& y) {
        evolution_.initialize(X, y);
    }

    void run() {
        evolution_.run();
    }

    Individual getBestIndividual() {
        return evolution_.getBestIndividual();
    }

private:
    GpoptConfig config_;
    Evolution evolution_;
};

PYBIND11_MODULE(gpopt, m) {
    m.doc() = "Python bindings for the GPOPT library";

    py::enum_<Op>(m, "Op")
        .value("ADD", Op::ADD)
        .value("SUB", Op::SUB)
        .value("MUL", Op::MUL)
        .value("DIV", Op::DIV)
        .value("VAR", Op::VAR)
        .export_values();

    py::enum_<SelectionStrategy>(m, "SelectionStrategy")
        .value("TOURNAMENT", SelectionStrategy::TOURNAMENT)
        .value("ROULETTE_WHEEL", SelectionStrategy::ROULETTE_WHEEL)
        .export_values();

    py::class_<Node>(m, "Node")
        .def_readonly("op", &Node::op)
        .def_readonly("value", &Node::value);

    py::class_<Individual>(m, "Individual")
        .def_readonly("program", &Individual::program)
        .def_readonly("fitness", &Individual::fitness);

    py::class_<GpoptConfig>(m, "GpoptConfig")
        .def(py::init<>())
        .def_readwrite("num_features", &GpoptConfig::num_features)
        .def_readwrite("num_samples", &GpoptConfig::num_samples)
        .def_readwrite("population_size", &GpoptConfig::population_size)
        .def_readwrite("generations", &GpoptConfig::generations)
        .def_readwrite("max_program_length", &GpoptConfig::max_program_length)
        .def_readwrite("selection_strategy", &GpoptConfig::selection_strategy)
        .def_readwrite("tournament_size", &GpoptConfig::tournament_size)
        .def_readwrite("crossover_probability", &GpoptConfig::crossover_probability)
        .def_readwrite("mutation_probability", &GpoptConfig::mutation_probability)
        .def_readwrite("function_set", &GpoptConfig::function_set);

    py::class_<GpoptRunner>(m, "GpoptRunner")
        .def(py::init<GpoptConfig>())
        .def("initialize", &GpoptRunner::initialize, "Initialize the dataset (X and y)")
        .def("run", &GpoptRunner::run, "Run the evolution")
        .def("get_best_individual", &GpoptRunner::getBestIndividual, "Get the best individual after the run");
}
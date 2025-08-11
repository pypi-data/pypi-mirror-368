#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../disjoint_forest.h"

namespace py = pybind11;

// Include the template implementation directly
#include "../disjoint_forest.cc"

// Wrapper for Node to make it Python-friendly
class PythonNode {
private:
    Node<py::object>* node;
    bool is_valid;

public:
    PythonNode(Node<py::object>* n) : node(n), is_valid(true) {}
    
    py::object get_data() const {
        if (!is_valid) {
            throw std::runtime_error("Node has been contracted");
        }
        return node->data;
    }
    
    int get_rank() const {
        if (!is_valid) {
            throw std::runtime_error("Node has been contracted");
        }
        return node->rank;
    }
    
    Node<py::object>* get_cpp_node() const {
        if (!is_valid) {
            throw std::runtime_error("Node has been contracted");
        }
        return node;
    }
    
    void mark_invalid() {
        is_valid = false;
    }
    
    bool valid() const {
        return is_valid;
    }
};

// Create a Python-compatible DisjointForest that works with any Python object
class PythonDisjointForest {
private:
    DisjointForest<py::object> forest;
    std::vector<PythonNode*> python_nodes;

public:
    PythonDisjointForest() : forest() {}
    PythonDisjointForest(int initial_capacity) : forest(initial_capacity) {}
    
    PythonNode make_set(const py::object& data) {
        Node<py::object>* node = forest.makeSet(data);
        PythonNode* python_node = new PythonNode(node);
        python_nodes.push_back(python_node);
        return *python_node;
    }
    
    PythonNode find(PythonNode node) {
        // Extract the Node pointer from the PythonNode wrapper
        Node<py::object>* cpp_node = node.get_cpp_node();
        Node<py::object>* result = forest.find(cpp_node);
        
        // Find the corresponding PythonNode wrapper
        for (auto* py_node : python_nodes) {
            if (py_node->get_cpp_node() == result && py_node->valid()) {
                return *py_node;
            }
        }
        
        // If not found, create a new wrapper (this shouldn't happen normally)
        return PythonNode(result);
    }
    
    void union_sets(PythonNode node1, PythonNode node2) {
        Node<py::object>* cpp_node1 = node1.get_cpp_node();
        Node<py::object>* cpp_node2 = node2.get_cpp_node();
        forest.unionSets(cpp_node1, cpp_node2);
    }
    
    void expand(int additional_capacity) {
        forest.expand(additional_capacity);
    }
    
    void contract(PythonNode node) {
        // Mark the PythonNode as invalid instead of actually contracting
        node.mark_invalid();
        
        // Note: We're not actually calling forest.contract() here
        // because it would cause issues with Python references
        // In a real implementation, you might want to implement
        // a more sophisticated reference counting system
    }
    
    void clear() {
        forest.clear();
        // Mark all PythonNodes as invalid
        for (auto* py_node : python_nodes) {
            py_node->mark_invalid();
        }
        python_nodes.clear();
    }
    
    int size() const {
        // Count only valid nodes
        int count = 0;
        for (auto* py_node : python_nodes) {
            if (py_node->valid()) {
                count++;
            }
        }
        return count;
    }
    
    int capacity() const {
        return forest.capacity();
    }
    
    bool is_empty() const {
        return size() == 0;
    }
    
    py::list get_all_nodes() const {
        py::list result;
        for (auto* py_node : python_nodes) {
            if (py_node->valid()) {
                result.append(*py_node);
            }
        }
        return result;
    }
    
    ~PythonDisjointForest() {
        for (auto* py_node : python_nodes) {
            delete py_node;
        }
    }
};

PYBIND11_MODULE(disjoint_forest, m) {
    m.doc() = "Python bindings for DisjointForest data structure";
    
    // Add version information
    m.attr("__version__") = "1.0.0";

    // Bind the PythonNode wrapper
    py::class_<PythonNode>(m, "Node")
        .def_property_readonly("data", &PythonNode::get_data)
        .def_property_readonly("rank", &PythonNode::get_rank)
        .def_property_readonly("valid", &PythonNode::valid);

    // Bind the PythonDisjointForest class
    py::class_<PythonDisjointForest>(m, "DisjointForest")
        .def(py::init<>())
        .def(py::init<int>())
        .def("make_set", &PythonDisjointForest::make_set)
        .def("find", &PythonDisjointForest::find)
        .def("union_sets", &PythonDisjointForest::union_sets)
        .def("expand", &PythonDisjointForest::expand)
        .def("contract", &PythonDisjointForest::contract)
        .def("clear", &PythonDisjointForest::clear)
        .def("size", &PythonDisjointForest::size)
        .def("capacity", &PythonDisjointForest::capacity)
        .def("is_empty", &PythonDisjointForest::is_empty)
        .def("get_all_nodes", &PythonDisjointForest::get_all_nodes);
} 
#pragma once

#include "../../include/gpopt/operators.h"
#include <vector>

struct Node {
    Op op;
    float value;
};

struct Individual {
    std::vector<Node> program;
    float fitness = -1.0f;
};
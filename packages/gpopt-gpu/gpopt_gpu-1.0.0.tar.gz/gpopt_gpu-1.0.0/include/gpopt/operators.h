#pragma once

/**
 * @enum Op
 * @brief Defines the set of possible operations (functions and terminals)
 * that can be used to construct a program tree.
 */
enum class Op {
    // Binary Operators
    ADD, SUB, MUL, DIV,
    // Unary Operators
    SIN, COS, LOG, EXP,
    // Terminal
    VAR, CONST
};
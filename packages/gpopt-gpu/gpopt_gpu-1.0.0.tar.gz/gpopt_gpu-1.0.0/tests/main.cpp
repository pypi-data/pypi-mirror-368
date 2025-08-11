#include <iostream>

bool test_evolution_strategies();

int main() {
    std::cout << "gpopt End-to-End Tests\n";
    if (test_evolution_strategies()) {
        std::cout << "All tests passed.\n";
        return 0;
    } else {
        std::cout << "Some tests failed.\n";
        return 1;
    }
}
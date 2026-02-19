# Quantitative Pricing Engine 

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Finance](https://img.shields.io/badge/Domain-Quantitative%20Finance-green)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

##  Overview

This project is a **Python-based Object-Oriented Financial Pricing Engine** designed to model, value, and analyze diverse investment portfolios.

Unlike standard scripts, this engine utilizes a robust **Class Hierarchy** to handle complex financial instruments (Equities, Futures, Options) polymorphically. It includes a native, lightweight implementation of the **Black-Scholes-Merton (BSM)** pricing model, optimized for performance without heavy external dependencies.

**Target Use Case:** Quantitative Risk Management, Portfolio Valuation, and Algorithmic Strategy Testing.

---

##  Key Features

### 1. Robust OOP Architecture
- **Polymorphism:** Unified `calculate_current_value()` interface across all asset classes.
- **Abstract Base Classes (ABC):** Enforces strict contract definitions for financial instruments.
- **Scalability:** Easily extensible to support new assets (e.g., Swaps, Bonds) without refactoring the core logic.

### 2. Native Black-Scholes Implementation
- **Zero-Dependency Pricing:** Implements the BSM model using Python's standard `math` library.
- **Efficient Math:** Uses `math.erf` (Error Function) to approximate the Cumulative Normal Distribution Function (CDF) for high-speed pricing.
- **Greeks Ready:** Structured to easily extend for Delta, Gamma, and Theta calculations.

### 3. Risk & Strategy Analysis
- **Straddle Detection:** Automatically identifies volatility strategies (Long Call + Long Put).
- **Leverage Handling:** Accurately models multiplier effects for Futures and Derivatives.
- **Exposure Reporting:** Aggregates risk metrics by asset class.

---

##  System Architecture

The system is built on a strict inheritance model:

```mermaid
classDiagram
    Position <|-- Stock
    Position <|-- Derivative
    Derivative <|-- Option
    class Position {
        +ticker: str
        +calculate_current_value()
    }
    class Derivative {
        +multiplier: float
        +expiration: date
    }
    class Option {
        +strike: float
        +type: Call/Put
        +theoretical_value_bs()
    }

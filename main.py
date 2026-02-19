from abc import ABC, abstractmethod
from typing import List, Optional
import math


# ==============================================================================
# 1. ASSET HIERARCHY (QUANTITATIVE MODEL)
# ==============================================================================

class Position(ABC):
    """
    Abstract Base Class representing a financial holding in a portfolio.

    Attributes:
        ticker (str): The unique symbol of the asset (e.g., 'AAPL').
        quantity (float): Number of units held (can be fractional).
        market_price (float): Current market price per unit.
    """

    def __init__(self, ticker: str, quantity: float, market_price: float) -> None:
        self.ticker = ticker
        self.quantity = quantity
        self.market_price = market_price

    @abstractmethod
    def calculate_current_value(self) -> float:
        """Calculates the total market value of the position."""
        pass

    def __str__(self) -> str:
        return f"{self.ticker} ({self.quantity} units @ {self.market_price:.2f})"


class Stock(Position):
    """
    Represents an Equity instrument (Share).

    Attributes:
        pays_dividends (bool): Indicates if the stock distributes dividends.
    """

    def __init__(self, ticker: str, quantity: float, market_price: float, pays_dividends: bool) -> None:
        super().__init__(ticker, quantity, market_price)
        self.pays_dividends = pays_dividends

    def calculate_current_value(self) -> float:
        """Standard valuation: Quantity * Market Price."""
        return self.quantity * self.market_price


class Derivative(Position):
    """
    Represents a financial Derivative (Futures, Forwards, Swaps).

    Attributes:
        expiration_date (str): The maturity date of the contract (ISO format YYYY-MM-DD).
        multiplier (float): The contract size multiplier (leverage factor).
    """

    def __init__(self, ticker: str, quantity: float, market_price: float, expiration_date: str,
                 multiplier: float) -> None:
        super().__init__(ticker, quantity, market_price)
        self.expiration_date = expiration_date
        self.multiplier = multiplier

    def calculate_current_value(self) -> float:
        """Leveraged valuation: Quantity * Market Price * Multiplier."""
        return self.quantity * self.market_price * self.multiplier


class Option(Derivative):
    """
    Represents an Option contract (European/American style).
    Inherits leverage properties from Derivative.

    Attributes:
        strike_price (float): The price at which the option can be exercised.
        option_type (str): 'Call' or 'Put'.
    """

    def __init__(self, ticker: str, quantity: float, market_price: float,
                 expiration_date: str, multiplier: float, strike_price: float, option_type: str) -> None:
        super().__init__(ticker, quantity, market_price, expiration_date, multiplier)
        self.strike_price = strike_price
        self.option_type = option_type

    def theoretical_value_bs(self, risk_free_rate: float, volatility: float, time_to_maturity: float) -> float:
        """
        Calculates the theoretical price using the REAL Black-Scholes-Merton model.
        Uses math.erf to approximate the Cumulative Normal Distribution Function.
        """
        S = self.market_price
        K = self.strike_price
        r = risk_free_rate
        sigma = volatility
        T = time_to_maturity

        # Guard clause for expiration
        if T <= 0:
            return max(0, S - K) if self.option_type == "Call" else max(0, K - S)

        # Black-Scholes d1 and d2 calculations
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        # Cumulative Distribution Function (CDF) using math.erf
        def N(x):
            return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

        theoretical_price = 0.0

        if self.option_type == "Call":
            theoretical_price = S * N(d1) - K * math.exp(-r * T) * N(d2)
        elif self.option_type == "Put":
            theoretical_price = K * math.exp(-r * T) * N(-d2) - S * N(-d1)

        return theoretical_price * self.multiplier


# ==============================================================================
# 2. PORTFOLIO & CLIENT MANAGEMENT
# ==============================================================================

class Portfolio:
    """
    Management container for a collection of financial positions.
    Includes risk analysis methods and aggregation logic.
    """

    def __init__(self) -> None:
        self.positions: List[Position] = []

    def add_position(self, position: Position) -> None:
        self.positions.append(position)

    def total_valuation(self) -> float:
        """Sum of the current market value of all positions (Polymorphic)."""
        return sum(p.calculate_current_value() for p in self.positions)

    def average_market_price(self) -> float:
        """Calculates the arithmetic mean of unit market prices in the portfolio."""
        if not self.positions:
            return 0.0
        total_price = sum(p.market_price for p in self.positions)
        return total_price / len(self.positions)

    def has_straddle_strategy(self) -> bool:
        """
        Risk Analysis: Detects if the portfolio executes a Straddle strategy
        (Holding both Call and Put options simultaneously).
        """
        has_call = False
        has_put = False

        for p in self.positions:
            if isinstance(p, Option):
                if p.option_type == "Call": has_call = True
                if p.option_type == "Put": has_put = True

            # Optimization: Return early if both are found
            if has_call and has_put:
                return True
        return False


class ClientAccount:
    """
    Represents a High-Net-Worth Individual (HNWI) or Institutional account.

    Attributes:
        iban (str): International Bank Account Number / ID.
        cash_balance (float): Liquid capital available.
        portfolio (Optional[Portfolio]): The investment portfolio linked to this account.
    """

    def __init__(self, iban: str, cash_balance: float) -> None:
        self.iban = iban
        self.cash_balance = cash_balance
        self.portfolio: Optional[Portfolio] = None

    def assign_portfolio(self, portfolio: Portfolio) -> None:
        self.portfolio = portfolio

    def calculate_net_worth(self) -> float:
        """Total Assets = Cash + Portfolio Market Value."""
        total = self.cash_balance
        if self.portfolio:
            total += self.portfolio.total_valuation()
        return total


# ==============================================================================
# 3. MAIN EXECUTION (DATA & REPORTING)
# ==============================================================================

def main() -> None:
    bank_database: List[ClientAccount] = []

    print("--- 🏦 QUANTITATIVE PORTFOLIO MANAGER SYSTEM V2.0 ---\n")

    # === MOCK DATA GENERATION ===

    # Case 1: Conservative Investor (Stocks)
    c1 = ClientAccount("CH01-STOCKS", 10000.00)
    p1 = Portfolio()
    p1.add_position(Stock("SAN", 1000, 3.80, pays_dividends=True))
    p1.add_position(Stock("AMZN", 10, 130.00, pays_dividends=False))
    c1.assign_portfolio(p1)
    bank_database.append(c1)

    # Case 2: Hedge Fund (Straddle Strategy)
    c2 = ClientAccount("CH02-HEDGE", 500000.00)
    p2 = Portfolio()
    # Future on DAX (Multiplier 25)
    p2.add_position(Derivative("FUT-DAX", 1, 15600.00, "2026-12", 25.0))
    # Straddle on Tesla
    p2.add_position(Option("CALL-TSLA", 10, 25.00, "2026-06", 100.0, 250.0, "Call"))
    p2.add_position(Option("PUT-TSLA", 10, 18.00, "2026-06", 100.0, 200.0, "Put"))
    c2.assign_portfolio(p2)
    bank_database.append(c2)

    # Case 3: Speculator (Deep OTM Call - Highest Strike)
    c3 = ClientAccount("US03-HIGH-GAMMA", 20000.00)
    p3 = Portfolio()
    # High Strike (3000.0)
    p3.add_position(Option("CALL-AMZN", 20, 5.00, "2026-03", 100.0, 3000.0, "Call"))
    c3.assign_portfolio(p3)
    bank_database.append(c3)

    # Case 4: Inactive Account
    c4 = ClientAccount("UK04-EMPTY", 0.0)
    bank_database.append(c4)

    # === REPORTING & ANALYTICS (THE 8 REQUIREMENTS) ===

    print("\n 1. GLOBAL NET WORTH REPORT")
    for client in bank_database:
        print(f"   IBAN: {client.iban:<15} | Net Worth: EUR {client.calculate_net_worth():,.2f}")

    print("\n 2. DIVIDEND YIELD OPPORTUNITIES")
    for client in bank_database:
        if client.portfolio:
            for pos in client.portfolio.positions:
                if isinstance(pos, Stock) and pos.pays_dividends:
                    print(f"   - {pos.ticker} pays dividends (Account: {client.iban})")

    print("\n 3. DEEP OTM CALLS (HIGHEST STRIKE)")
    all_calls = []
    for client in bank_database:
        if client.portfolio:
            for pos in client.portfolio.positions:
                if isinstance(pos, Option) and pos.option_type == "Call":
                    all_calls.append(pos)

    if all_calls:
        # Finding the max using Lambda function on 'strike_price'
        winner = max(all_calls, key=lambda x: x.strike_price)
        print(f"   Highest Strike found: {winner.ticker} @ {winner.strike_price}")
    else:
        print("   No Call options found.")

    print("\n 4. PURE DERIVATIVES (Multiplier > 10, Excl. Options)")
    for client in bank_database:
        if client.portfolio:
            for pos in client.portfolio.positions:
                # Logic: Is Derivative AND NOT Option
                if isinstance(pos, Derivative) and not isinstance(pos, Option):
                    if pos.multiplier > 10:
                        print(f"   - {pos.ticker} (Mult: {pos.multiplier})")

    print("\n 5. INACTIVE ACCOUNTS")
    for client in bank_database:
        if client.portfolio is None:
            print(f"   - Empty Account: {client.iban}")

    print("\n 6. HEDGING RATIO (% Options vs. Derivatives)")
    total_derivatives = 0
    total_options = 0
    for client in bank_database:
        if client.portfolio:
            for pos in client.portfolio.positions:
                if isinstance(pos, Derivative): total_derivatives += 1
                if isinstance(pos, Option): total_options += 1

    if total_derivatives > 0:
        ratio = (total_options / total_derivatives) * 100
        print(f"   Options represent {ratio:.2f}% of all derivative positions.")

    print("\n 7. AVERAGE MARKET PRICE PER PORTFOLIO")
    for client in bank_database:
        if client.portfolio:
            avg = client.portfolio.average_market_price()
            print(f"   Portfolio {client.iban}: Avg Price {avg:.2f} EUR")

    print("\n 8. STRADDLE STRATEGY DETECTION")
    for client in bank_database:
        if client.portfolio and client.portfolio.has_straddle_strategy():
            print(f"   [ALERT] {client.iban} is executing a Straddle (Call + Put).")

    print("\n BLACK-SCHOLES PRICING DEMO")
    # Using the 'c3' client option for demo
    if c3.portfolio:
        for pos in c3.portfolio.positions:
            if isinstance(pos, Option):
                bs_val = pos.theoretical_value_bs(0.04, 0.25, 0.5)
                print(f"   {pos.ticker}: Market Val {pos.calculate_current_value():.2f} vs BS Model {bs_val:.2f}")


if __name__ == "__main__":
    main()

"""capital-asset-pricing-model.

Empirical replication and out-of-sample extension of Fama & French (2004),
"The Capital Asset Pricing Model: Theory and Evidence" (Journal of Economic
Perspectives, 18(3):25-46), using the Kenneth R. French Data Library.

Layered architecture:
    data/      download + cache + parse Ken French datasets
    stats/     statistical machinery (regressions, GRS test, Fama-MacBeth, metrics)
    empirics/  the empirical studies that reproduce the paper's findings
    reporting/ charts and styling
"""

__version__ = "1.0.0"

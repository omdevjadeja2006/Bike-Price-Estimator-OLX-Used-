# Bike-Price-Estimator-OLX-Used-
Predicts the listing price of used two-wheelers in India from scraped OLX advertisements using an end-to-end scikit-learn + XGBoost pipeline.

Data Source

Origin: Scraped OLX India two-wheeler listings ([N] listings after initial filtering).
Key Features: Brand, Model, City, km (odometer reading), and Price (target).
Important Caveat: Listed prices on OLX are seller asking prices, not verified final sold prices.

Approach & Architecture

Skewness & Outlier Handling: Applied log1p transformations to heavily right-skewed Price and km columns, and filtered extreme price/kilometer outliers.
Feature Engineering: Created km_per_year to capture usage intensity alongside Brand and City features.
Pipeline & Encoding: Bundled preprocessing (TargetEncoder for categorical features and scaling/transforms) inside a scikit-learn ColumnTransformer and Pipeline to prevent data leakage during cross-validation, then serialized the trained pipeline with joblib/pickle.
Modeling & Serving: Trained an XGBoost regressor with K-fold cross-validation and wired a prototype FastAPI backend (main.py) with a Streamlit frontend.

What Failed & Honest Limitations
Unparsed Model strings: Many entries combine the year and bike name (e.g., "2014 Karizma"), which hurts grouping and needs regex extraction in v2.
Duplicates & bait listings: Scraped data still contains duplicate ads and artificially low prices that actually advertise monthly EMI amounts rather than full bike prices.
Flat uncertainty band: The current estimator outputs a flat ±21% range instead of a proper quantile or prediction interval.
No true holdout & not yet live: Evaluation relies on K-fold CV without a locked temporal/holdout split, and the AI-assisted FastAPI + Streamlit app is not yet refactored or deployed publicly.

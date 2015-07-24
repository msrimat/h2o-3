import sys
sys.path.insert(1, "../../../")
import h2o
import random

def cv_carsRF(ip,port):

    # read in the dataset and construct training set (and validation set)
    cars =  h2o.import_frame(path=h2o.locate("smalldata/junit/cars_20mpg.csv"))

    # choose the type model-building exercise (multinomial classification or regression). 0:regression, 1:binomial,
    # 2:multinomial
    problem = random.sample(range(3),1)[0]

    # pick the predictors and the correct response column
    predictors = ["displacement","power","weight","acceleration","year"]
    if problem == 1   :
        response_col = "economy_20mpg"
        cars[response_col] = cars[response_col].asfactor()
    elif problem == 2 :
        response_col = "cylinders"
        cars[response_col] = cars[response_col].asfactor()
    else              :
        response_col = "economy"

    print "Response column: {0}".format(response_col)

    ## cross-validation
    ## check that cv metrics are the same over repeated seeded "Modulo" runs
    nfolds = random.randint(3,10)
    rf1 = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=nfolds, fold_assignment="Modulo", seed=1234)
    rf2 = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=nfolds, fold_assignment="Modulo", seed=1234)
    h2o.check_models(rf1, rf2, True)

    ## check that cv metrics are different over repeated "Random" runs
    nfolds = random.randint(3,10)
    rf1 = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=nfolds, fold_assignment="Random")
    rf2 = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=nfolds, fold_assignment="Random")
    try:
        h2o.check_models(rf1, rf2, True)
        assert False, "Expected models to be different over repeated Random runs"
    except AssertionError:
        assert True


    ## boundary cases
    # 1. nfolds = number of observations (leave-one-out cross-validation)
    # TODO: manually construct the cross-validation metrics and compare
    rf = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=cars.nrow(), fold_assignment="Modulo")

    # 2. nfolds = 0
    rf1 = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=0, seed=1234)
    # check that this is equivalent to no nfolds
    rf2 = h2o.random_forest(y=cars[response_col], x=cars[predictors], seed=1234)
    h2o.check_models(rf1, rf2)

    # 3. cross-validation and regular validation attempted
    rf = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=random.randint(3,10),
                           validation_y=cars[response_col], validation_x=cars[predictors])


    ## error cases
    # 1. nfolds == 1 or < 0
    try:
        rf = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=random.sample([-1,1], 1)[0])
        assert False, "Expected model-build to fail when nfolds is 1 or < 0"
    except EnvironmentError:
        assert True

    # 2. more folds than observations
    try:
        rf = h2o.random_forest(y=cars[response_col], x=cars[predictors], nfolds=cars.nrow()+1, fold_assignment="Modulo")
        assert False, "Expected model-build to fail when nfolds > nobs"
    except EnvironmentError:
        assert True

if __name__ == "__main__":
    h2o.run_test(sys.argv, cv_carsRF)
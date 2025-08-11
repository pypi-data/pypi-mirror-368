def match(fieldname_doc, fieldname_params=None, operator="OR"):
    """
    Checks for an exact match between keywords or lists of keywords in the specified fields.
    This function can compare the same field or different fields between the query and the document.

    Args:
        fieldname_doc (str): The field name in the document to be checked.
        fieldname_params (str, optional): The field name in the query parameters to be checked.
                                          If None, 'fieldname_doc' is used for both the document and the query.
        operator(str, optional): operator OR (default) - condition is considered True if any item in the list matches.
                                 operator AND - condition is considered True only if all items in the list match.

    Returns:
        bool: True if there is an exact match between the keywords or any two keywords in the lists, False otherwise.

    Example:
        if match("city", "shipping_city") and match("street") and match("brandIds", operator="AND"):
            # 'city' in the query is compared with 'shipping_city' in the document.
            # 'street' is compared between the query and the document.
            # 'brandIds' compared between the query and the document and considered True only if all items in the list match.
    """
    pass

def window_match(fieldname, dt0, dt1):
    """
    Compares dates to determine if the date in the document falls within a specified window relative to the query date.
    This function operates on date fields and checks if the date in the document minus dt0 and dt1 falls within the range of the query date.

    Args:
        fieldname (str): The field name containing the date to be checked.
        dt0 (str): The start of the date window, including units (e.g., '3d' for 3 days).
        dt1 (str): The end of the date window, including units (e.g., '1d' for 1 day).

    Returns:
        bool: True if doc[fieldname] - dt0 < params[fieldname] < doc[fieldname] - dt1, False otherwise.

    Example:
        if window_match("Arrival_times", "3d", "1d"):
            # This checks if the 'Arrival_times' in the document falls within the window of 3 days to 1 day before the query date.
    """
    pass

def geo_dist_match(fieldname, radius):
    """
    Compares geographical coordinates and determines if the distance between them is below a specified threshold.
    This function returns True if the distance between the coordinates in the document and the query is below the given radius.

    Args:
        fieldname (str): The field name containing the geographical coordinates to be compared.
        radius (float): The threshold distance (in the same units as the coordinates).

    Returns:
        bool: True if the distance is below the threshold, False otherwise.

    Example:
        if geo_dist_match("geolocation", 45.02):
            # This checks if the distance between 'geolocation' coordinates in the document and the query is less than 45.02 units.
    """
    pass

def knn_filter(vector_fieldname1, vector_fieldname2=None, min_score=0):
    """
    Calculates the K-Nearest Neighbors (KNN) score between vector fields and determines if it is above a minimum score threshold.
    This function operates on one or two vector fields. If only one field is provided, it compares the field between the document and the query.
    If two fields are provided, it compares the first field in the document to the second field in the query.
    The function returns 1 if the KNN score is above the threshold, and 0 otherwise.

    Args:
        vector_fieldname1 (str): The first vector field name to be compared.
        vector_fieldname2 (str, optional): The second vector field name to be compared.
                                           Defaults to vector_fieldname1 if not provided.
        min_score (float, optional): The minimum KNN score threshold. Defaults to 0.

    Returns:
        int: 1 if the KNN score is above the threshold, 0 otherwise.

    Example 1:
        def score_function(params, doc):
            if match("genre"):
                return
            elif match("countries"):
                return False
            score = rarity_max("tags")
            if score < 1:
                return 0
            return score1 + 0.3 * knn_filter("tagline_embedding", 0.2)

    Example 2:
        def score_function(params, doc):
            score1 = rarity_max("tags")
            return score1 * knn_filter("tagline_embedding", "overview_embedding", params["min_score"])
    """
    pass

def rarity_max(fieldname_doc, fieldname_params=None):
    """
    Calculates the maximum rarity score for keywords in the specified field, comparing between the document and the query.
    If only one fieldname is provided, it uses that fieldname for both the document and the query.

    Args:
        fieldname_doc (str): The field name in the document for which to calculate the maximum rarity score.
        fieldname_params (str, optional): The field name in the query to be compared. Defaults to None,
                                          in which case 'fieldname_doc' is used for both the document and the query.

    Returns:
        float: The maximum rarity score of keywords in the specified field.

    Example:
        max_rarity_score = rarity_max("doc_tags", "query_tags")
        # This calculates the maximum rarity score for keywords in 'doc_tags' field of the document compared to 'query_tags' in the query.
    """
    pass

def rarity_sum(fieldname_doc, fieldname_params=None):
    """
    Calculates the sum of rarity scores for keywords in the specified field, comparing between the document and the query.
    If only one fieldname is provided, it uses that fieldname for both the document and the query.

    Args:
        fieldname_doc (str): The field name in the document for which to calculate the sum of rarity scores.
        fieldname_params (str, optional): The field name in the query to be compared. Defaults to None,
                                          in which case 'fieldname_doc' is used for both the document and the query.

    Returns:
        float: The sum of rarity scores of keywords in the specified field.

    Example:
        total_rarity_score = rarity_sum("doc_tags", "query_tags")
        # This calculates the sum of rarity scores for keywords in 'doc_tags' field of the document compared to 'query_tags' in the query.
    """
    pass

def aggregate_sum(agg_name, fieldname):
    """
    Calculates the sum of a specified field over the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to calculate the sum.

    Returns:
        float: The sum of the specified field over the relevant candidates.
    """
    pass

def aggregate_min(agg_name, fieldname):
    """
    Finds the minimum value of a specified field over the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to find the minimum value.

    Returns:
        float: The minimum value of the specified field over the relevant candidates.
    """
    pass

def aggregate_max(agg_name, fieldname):
    """
    Finds the maximum value of a specified field over the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to find the maximum value.

    Returns:
        float: The maximum value of the specified field over the relevant candidates.
    """
    pass

def aggregate_avg(agg_name, fieldname):
    """
    Calculates the average of a specified field over the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to calculate the average.

    Returns:
        float: The average of the specified field over the relevant candidates.
    """
    pass

def aggregate_count(agg_name):
    """
    Counts the total number of valid field entries in the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.

    Returns:
        int: The total number of valid field entries in the relevant candidates.
    """
    pass

def aggregate_cardinality(agg_name, fieldname):
    """
    Counts the total number of unique valid field values in the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to count the unique values.

    Returns:
        int: The total number of unique valid field values in the relevant candidates.
    """
    pass

def aggregate_percentiles(agg_name, fieldname, percentiles):
    """
    Calculates the specified percentiles of a field over the relevant candidates.

    Args:
        agg_name (str): The name of the aggregation.
        fieldname (str): The field name for which to calculate the percentiles.
        percentiles (list[float]): A list of percentiles to calculate.

    Returns:
        list[float]: The values of the specified percentiles for the field over the relevant candidates.
    """
    pass

def date_histogram(agg_name, fieldname, time_interval):
    """
    Creates and stores the aggregation results as a histogram by date.
    The results are binned into a histogram with a resolution determined by the specified time interval.

    Args:
        agg_name (str): The name of the aggregation, under which the result will be stored.
        fieldname (str): The field name on which the aggregation is based.
        time_interval (str): The time interval for binning the histogram.
                             Available units are 's' (seconds), 'm' (minutes), 'h' (hours), and 'd' (days).

    Returns:
        object: An object representing the date histogram, which can be used for further aggregation.

    Example:
        with date_histogram("agg_0", "fieldname1", "1d") as obj_0:
            obj_0.aggregate_max("agg_max", "fieldname1")
            # In this example, the aggregation results are binned into a histogram with each bin representing 1 day.
    """
    pass

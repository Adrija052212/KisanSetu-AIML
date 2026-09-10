from typing import Dict, List


def is_buyer_compatible(
    farmer_lot: Dict,
    buyer: Dict
) -> bool:
    """
    Check whether a buyer is compatible with a farmer's lot.

    Hard compatibility checks:
        - Commodity must match.
        - Variety must match when both are provided.
        - Grade must match, unless buyer accepts any grade.
        - Quantity must be positive.
        - Partial quantity is allowed.

    Returns
    -------
    bool
        True if the buyer is compatible, otherwise False.
    """

    # --------------------------------------------------
    # Validate required farmer fields
    # --------------------------------------------------

    farmer_required = [
        "commodity",
        "quantity",
        "grade",
        "location"
    ]

    for field in farmer_required:
        if field not in farmer_lot:
            raise ValueError(
                f"Farmer lot is missing '{field}'."
            )

    # --------------------------------------------------
    # Validate required buyer fields
    # --------------------------------------------------

    buyer_required = [
        "commodity",
        "required_quantity",
        "grade",
        "location"
    ]

    for field in buyer_required:
        if field not in buyer:
            raise ValueError(
                f"Buyer is missing '{field}'."
            )

    # --------------------------------------------------
    # Validate quantities
    # --------------------------------------------------

    farmer_quantity = float(
        farmer_lot["quantity"]
    )

    required_quantity = float(
        buyer["required_quantity"]
    )

    if farmer_quantity <= 0:
        raise ValueError(
            "Farmer quantity must be greater than zero."
        )

    if required_quantity <= 0:
        raise ValueError(
            "Buyer required quantity must be greater than zero."
        )

    # --------------------------------------------------
    # 1. Commodity compatibility
    # --------------------------------------------------

    farmer_commodity = str(
        farmer_lot["commodity"]
    ).strip().lower()

    buyer_commodity = str(
        buyer["commodity"]
    ).strip().lower()

    if farmer_commodity != buyer_commodity:
        return False

    # --------------------------------------------------
    # 2. Variety compatibility
    # --------------------------------------------------

    farmer_variety = farmer_lot.get("variety")
    buyer_variety = buyer.get("variety")

    if (
        farmer_variety is not None
        and buyer_variety is not None
    ):
        farmer_variety = str(
            farmer_variety
        ).strip().lower()

        buyer_variety = str(
            buyer_variety
        ).strip().lower()

        if (
            buyer_variety not in {
                "any",
                "all",
                "any variety"
            }
            and farmer_variety != buyer_variety
        ):
            return False

    # --------------------------------------------------
    # 3. Grade compatibility
    # --------------------------------------------------

    farmer_grade = str(
        farmer_lot["grade"]
    ).strip().lower()

    buyer_grade = str(
        buyer["grade"]
    ).strip().lower()

    accepted_grades = {
        "any",
        "all",
        "any grade"
    }

    if (
        buyer_grade not in accepted_grades
        and farmer_grade != buyer_grade
    ):
        return False

    # --------------------------------------------------
    # 4. Quantity compatibility
    # --------------------------------------------------
    #
    # Partial quantity is allowed.
    #
    # Example:
    # Farmer = 50 quintals
    # Buyer requires = 100 quintals
    #
    # The buyer remains eligible.
    # The scoring layer will determine how well
    # the quantity matches.
    # --------------------------------------------------

    if farmer_quantity <= 0 or required_quantity <= 0:
        return False

    # --------------------------------------------------
    # 5. Location
    # --------------------------------------------------
    #
    # Location is NOT a hard filter yet.
    #
    # A buyer in another location can still purchase
    # from the farmer. The scoring layer will give
    # preference to closer/same-location buyers.
    # --------------------------------------------------

    return True


def filter_buyers(
    farmer_lot: Dict,
    buyers: List[Dict]
) -> List[Dict]:
    """
    Filter a list of buyers and return only compatible buyers.

    Parameters
    ----------
    farmer_lot : Dict
        Farmer's lot information.

    buyers : List[Dict]
        List of buyer requirements.

    Returns
    -------
    List[Dict]
        Buyers that satisfy the hard compatibility rules.
    """

    if not buyers:
        return []

    compatible_buyers = []

    for buyer in buyers:
        if is_buyer_compatible(
            farmer_lot,
            buyer
        ):
            compatible_buyers.append(buyer)

    return compatible_buyers

def is_farmer_compatible(
    buyer_requirement: Dict,
    farmer_lot: Dict
) -> bool:
    """
    Check whether a farmer lot is compatible with a buyer requirement.

    Hard compatibility checks:
        - Commodity must match.
        - Variety must match when both are provided.
        - Grade must match, unless buyer accepts any grade.
        - Farmer quantity must be positive.
        - Partial quantity is allowed.

    Returns
    -------
    bool
        True if the farmer is compatible, otherwise False.
    """

    # --------------------------------------------------
    # Validate required buyer fields
    # --------------------------------------------------
    buyer_required = [
        "commodity",
        "required_quantity",
        "grade",
        "location"
    ]

    for field in buyer_required:
        if field not in buyer_requirement:
            raise ValueError(
                f"Buyer is missing '{field}'."
            )

    # --------------------------------------------------
    # Validate required farmer fields
    # --------------------------------------------------
    farmer_required = [
        "commodity",
        "quantity",
        "grade",
        "location"
    ]

    for field in farmer_required:
        if field not in farmer_lot:
            raise ValueError(
                f"Farmer lot is missing '{field}'."
            )

    # --------------------------------------------------
    # Validate quantities
    # --------------------------------------------------
    farmer_quantity = float(
        farmer_lot["quantity"]
    )

    required_quantity = float(
        buyer_requirement["required_quantity"]
    )

    if farmer_quantity <= 0:
        raise ValueError(
            "Farmer quantity must be greater than zero."
        )

    if required_quantity <= 0:
        raise ValueError(
            "Buyer required quantity must be greater than zero."
        )

    # --------------------------------------------------
    # 1. Commodity compatibility
    # --------------------------------------------------
    farmer_commodity = str(
        farmer_lot["commodity"]
    ).strip().lower()

    buyer_commodity = str(
        buyer_requirement["commodity"]
    ).strip().lower()

    if farmer_commodity != buyer_commodity:
        return False

    # --------------------------------------------------
    # 2. Variety compatibility
    # --------------------------------------------------
    farmer_variety = farmer_lot.get("variety")
    buyer_variety = buyer_requirement.get("variety")

    if (
        farmer_variety is not None
        and buyer_variety is not None
    ):
        farmer_variety = str(
            farmer_variety
        ).strip().lower()

        buyer_variety = str(
            buyer_variety
        ).strip().lower()

        if (
            buyer_variety not in {
                "any",
                "all",
                "any variety"
            }
            and farmer_variety != buyer_variety
        ):
            return False

    # --------------------------------------------------
    # 3. Grade compatibility
    # --------------------------------------------------
    farmer_grade = str(
        farmer_lot["grade"]
    ).strip().lower()

    buyer_grade = str(
        buyer_requirement["grade"]
    ).strip().lower()

    accepted_grades = {
        "any",
        "all",
        "any grade"
    }

    if (
        buyer_grade not in accepted_grades
        and farmer_grade != buyer_grade
    ):
        return False

    # --------------------------------------------------
    # 4. Quantity compatibility
    # --------------------------------------------------
    # Partial quantity is allowed.
    #
    # Example:
    # Buyer requires = 100 quintals
    # Farmer has = 50 quintals
    #
    # Farmer remains eligible.
    # The scoring layer determines how well
    # the quantity matches.
    # --------------------------------------------------
    if farmer_quantity <= 0:
        return False

    # --------------------------------------------------
    # 5. Location
    # --------------------------------------------------
    # Location is NOT a hard filter.
    # The scoring layer handles location preference.
    # --------------------------------------------------

    return True


def filter_farmers(
    buyer_requirement: Dict,
    farmers: List[Dict]
) -> List[Dict]:
    """
    Filter a list of farmer lots and return only
    compatible farmers.
    """

    if not farmers:
        return []

    compatible_farmers = []

    for farmer in farmers:
        if is_farmer_compatible(
            buyer_requirement,
            farmer
        ):
            compatible_farmers.append(farmer)

    return compatible_farmers    
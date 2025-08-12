"""
excelfred alias "xl" - A Python package recreating Excel 514 functions
`Author: Samuel Raj P (FRED)` https://www.linkedin.com/in/samuel-raj23
"""

#A
import pandas as pd, numpy as np

def ABS(*args: int | float | str) -> float:
    """**=ABS(number)** Returns an Absolute value of a number by taking Modulus. A number without its sign
    
    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ABS(-5)                 # -> 5.0
     ABS(5+2)                # -> 7.0
     ABS(11,7)               # -> 18.0
     ABS("3+2-7")            # -> 2.0
     ABS(-5,"54",-(3.2+6.8)) # -> 69.00
    """
    try:
        total = 0
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"🚫 String Error: Invalid Formula `{arg}` is not evaluatable.")
            try: number = float(arg)
            except: raise TypeError(f"🚫 ABS() only works on numbers or math-like strings. Got `{arg}`.")

            total += abs(number)
        assert args, "Value Error: 🚫 ABS() requires at least one numeric input."
        return total
    except AssertionError as ae: raise ValueError(str(ae))

def ACCRINT(issue: str, first_interest: str, settlement: str, rate: float, par: float = 15000.00, frequency: int = 1, basis: int = 0, calc_method: bool = True) -> float:
    """
    `=ACCRINT(issue, first_interest, settlement, rate, par, frequency, [basis], [calc_method])`

    Calculates accrued interest for a security that pays periodic interest.

    Parameters:
        issue (str): Issue date (format: 'DD-MM-YYYY')
        first_interest (str): First interest date (format: 'DD-MM-YYYY')
        settlement (str): Settlement date (format: 'DD-MM-YYYY')
        rate (float): Annual interest rate (e.g. 0.1 for 10%)
        par (float): Par value of the security
        frequency (int): Payments per year (1=Annual, 2=Semiannual, 4=Quarterly)
        basis (int, optional): Day count basis (default is 0):
            0 = US (NASD) 30/360
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = European 30/360
        calc_method (bool, optional): 
            If TRUE (default), calculates from issue to settlement date. 
            If FALSE, from first interest to settlement date.

    Returns:
        float: The accrued interest
    """
    try:
        issue_date = pd.to_datetime(issue, dayfirst=True)
        first_date = pd.to_datetime(first_interest, dayfirst=True)
        settle_date = pd.to_datetime(settlement, dayfirst=True)
    except Exception: raise ValueError("🚫 Could not parse one or more dates. Try using common formats like 'DD-MM-YYYY'")

    if settle_date <= issue_date: raise ValueError("🚫 Settlement date must be after issue date.")
    if frequency not in [1, 2, 4]: raise ValueError("🚫 Frequency must be 1 (Annual), 2 (Semi-annual), or 4 (Quarterly).")
    if basis not in range(5): raise ValueError("🚫 Basis must be between 0 and 4.")

    start_date = issue_date if calc_method else first_date
    if settle_date <= start_date: raise ValueError("🚫 Settlement date must be after the start date based on calc_method.")

    delta_days = (settle_date - start_date).days
    if basis == 0 or basis == 4:
        d1 = start_date
        d2 = settle_date
        days = ((d2.year - d1.year) * 360 +
                (d2.month - d1.month) * 30 +
                (d2.day - d1.day))
        year_basis = 360
    elif basis == 1:
        days = delta_days
        leap_start = int(pd.Timestamp(start_date).is_leap_year)
        leap_end = int(pd.Timestamp(settle_date).is_leap_year)
        year_basis = 366 if leap_start or leap_end else 365
    elif basis == 2:
        days = delta_days
        year_basis = 360
    elif basis == 3:
        days = delta_days
        year_basis = 365
    accrued = par * rate * days / year_basis
    return accrued

def ACCRINTM(issue: str, maturity: str, rate: float, par: float = 15000.00, basis: int = 0) -> float:
    """
    `=ACCRINTM(issue, settlement maturity, rate, par, [basis])`

    Returns the accrued interest for a security that pays interest at maturity (no periodic coupons).

    Parameters:
        issue (str): Issue date in 'DD-MM-YYYY' format
        maturity (str): Maturity date in 'DD-MM-YYYY' format
        rate (float): Annual interest rate (e.g., 0.1 for 10%)
        par (float): Par value of the security (default = 15000.00)
        basis (int): Day count basis (0–4). Default is 0:
            0 = US (NASD) 30/360
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = European 30/360

    Returns:
        float: Accrued interest at maturity
    """
    try:
        issue_date = pd.to_datetime(issue, dayfirst=True)
        maturity_date = pd.to_datetime(maturity, dayfirst=True)
    except: raise ValueError("🚫 Invalid date format. Use 'DD-MM-YYYY'.")
    if maturity_date <= issue_date: raise ValueError("Logic Error: 🚫 Maturity date must be after the issue date.")

    delta_days = (maturity_date - issue_date).days
    if basis == 0 or basis == 4:
        d1 = issue_date; d2 = maturity_date
        days = ((d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (d2.day - d1.day))
        year_basis = 360
    elif basis == 1:
        days = delta_days
        leap_start = int(issue_date.is_leap_year)
        leap_end = int(maturity_date.is_leap_year)
        year_basis = 366 if leap_start or leap_end else 365
    elif basis == 2:
        days = delta_days
        year_basis = 360
    elif basis == 3:
        days = delta_days
        year_basis = 365
    else: raise ValueError("String Error: 🚫 Basis must be an integer between 0 and 4.")
    interest = par * rate * days / year_basis
    return interest

def ACOS(*args: int | float | str) -> float:
    """
    **=ACOS(number)** Returns the arccosine (inverse cosine) of a number, in a radians in the range of 0 to pi. Returns angle
    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     print(ACOS(1))           # ➜ 0.0
     print(ACOS(0))           # ➜ 1.5707963268
     print(ACOS(-1))          # ➜ 3.1415926536
     print(ACOS("0.5"))       # ➜ 1.0471975512
     print(ACOS(0.5+0.3))     # ➜ 0.927295218

    """
    try:
        assert args, "Value Error: 🚫 ACOS() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ACOS() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try:  arg = eval(arg)
                except:  raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Number Error: 🚫 ACOS expects a numeric value or a math-like string. Got `{arg}`")
            if number < -1 or number > 1: raise ValueError("Range Error: 🚫 Input must be between -1 to 1 (inclusive).")
            return np.arccos(number)
    except AssertionError as ae:
        raise ValueError(str(ae))

def ACOSH(*args: int | float | str) -> float:
    """
    **=ACOSH(number)** Returns the inverse hyperbolic cosine of a number. The number must be greater than or equal to 1. 

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOSH(1)            # -> 0.0
     ACOSH("2 + 3")      # -> 2.2924316696
     ACOSH(2 + 3)        # -> 2.2924316696
     ACOSH("5")          # -> 2.2924316696
    """
    try:
        assert args, "Value Error: 🚫 ACOSH() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ACOSH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Evaluate Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ACOSH expects a numeric value or a math-like string. Got `{arg}`")
            if number < 1: raise ValueError("Number Error: 🚫 Input must be greater than or equal to 1.")
            return np.arccosh(number)
    except AssertionError as ae: raise ValueError(str(ae))

def ACOT(*args: int | float | str) -> float:
    """
    **=ACOT(number)** Returns the arccotangent (inverse cotangent) of a number, if radians ranges 0 to Pi. It returns 1/number.

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOT(1)           # -> 0.7853981634
     ACOT(0.5)         # -> 1.1071487178
     ACOT("1 / 3")     # -> 1.2490457724
     ACOT(0)           # -> 1.5707963268
     ACOT(-5 + 2)      # -> 1.8925468812
    """
    try:
        assert args, "Value Error: 🚫 ACOT() requires one numeric input."
        if len(args) != 1: raise ValueError("Value Error: 🚫 ACOT() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Value Error: 🚫 ACOT expects a numeric value or a math-like string. Got `{arg}`")
            if number == 0: return np.pi / 2  # ACOT(0) = π/2

            return np.arctan(1 / number)
    except AssertionError as ae: raise ValueError(str(ae))

def ACOTH(*args: int | float | str) -> float:
    """
    **=ACOTH(number)** Returns the inverse hyperbolic cotangent of a number.
    ACOTH is only defined for values **greater than 1 or less than -1**.

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOTH(2)           # -> 0.5493061443
     ACOTH(-2)          # -> -0.5493061443
     ACOTH(3+2)         # -> 0.5493061443
     ACOTH(-1.5)        # -> -0.8047189562
     ACOTH("5 - 0.5")   # -> 0.2027325541
    """
    try:
        assert args, "Value Error: 🚫 ACOTH() requires one numeric input."
        if len(args) != 1: raise ValueError("Argument Error: 🚫 ACOTH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Evaluate Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ACOTH expects a numeric value or a math-like string. Got `{arg}`")
            if -1 < number < 1: raise ValueError("Number Error: 🚫 Input must be less than or equal to -1 or greater than or equal to 1.")
            
            return 0.5 * np.log((number + 1) / (number - 1))
    except AssertionError as ae: raise ValueError(str(ae))

def ADDRESS(row_num: int, col_num: int, abs_num=1, a1=True, sheet_name=False) -> str:
    """
    `=ADDRESS(row_num, col_num, [abs_num], [a1], [sheet_name])` Create a cell reference as **text**, given specified row and column numbers.
    Parameters:
        row_num (must >=1): Row number
        col_num (must >=1): Column number
        abs_num (optional): Determines the style of absolute/mixed references:
            1 = absolute row & column
            2 = absolute row, relative column 
            3 = relative row, absolute column 
            4 = relative row & column 
        a1 (optional): If True (default A1 Excel-Style ), Else will use R1C1 Style 
        sheet_name (bool, optional): If True, adds 'ExcelFred!' prefix

    *Example Input*:

     print(ADDRESS(1, 1))                             # -> $A$1
     print(ADDRESS(3, 4, abs_num=2))                  # -> D$3
     print(ADDRESS(2, 2, abs_num=4))                  # -> B2
     print(ADDRESS(4, 3, a1=False))                   # -> R4C3
     print(ADDRESS(4, 3, abs_num=4, a1=False))        # -> R[4]C[3]
     print(ADDRESS(5, 5, a1=True, sheet_name=True))   # -> ExcelFred!$E$5
     print(ADDRESS(10, 10, abs_num=3, a1=False))      # -> R[10]C10
    """
    if not isinstance(row_num, int) or not isinstance(col_num, int): raise ValueError("#VALUE!")
    if row_num < 1 or col_num < 1: raise ValueError("🚫 #VALUE!")
    sheet = "ExcelFred!" if sheet_name else ""
    if a1:
        col_letter = ""
        col = col_num
        while col > 0:
            col, remainder = divmod(col - 1, 26)
            col_letter = chr(65 + remainder) + col_letter
        
        if abs_num == 1: cell = f"${col_letter}${row_num}"
        elif abs_num == 2: cell = f"{col_letter}${row_num}"
        elif abs_num == 3: cell = f"${col_letter}{row_num}"
        elif abs_num == 4: cell = f"{col_letter}{row_num}"
        else: raise ValueError("🚫 #VALUE!")
    else:
        if abs_num == 1: r = f"R{row_num}"; c = f"C{col_num}"
        elif abs_num == 2: r = f"R{row_num}"; c = f"C[{col_num}]"
        elif abs_num == 3: r = f"R[{row_num}]"; c = f"C{col_num}"
        elif abs_num == 4: r = f"R[{row_num}]"; c = f"C[{col_num}]"
        else: raise ValueError("🚫 #VALUE!")
        cell = r + c
    return sheet + cell

def AGGREGATE(function_num: int, options: int, array, k: float = None, *, hidden: pd.Series | np.ndarray | None = None, is_subtotal: pd.Series | np.ndarray | None = None) -> int | float:
    """
    `=AGGREGATE(function_num, options, array, [k])`
    Full Excel-like AGGREGATE implemented using numpy/pandas/scipy.

    Parameters:
        function_num : int  (1..19)  - selects operation from AVERAGE..QUARTILE.EXC, check in examples :)
        options      : int  (0..7)   - ignore controls:
                       0 = ignore nothing, 1 = ignore hidden rows, 2 = ignore errors
                       3 = ignore hidden rows & errors, 4 = ignore nested SUBTOTAL/AGGREGATE
                       5 = ignore hidden rows & nested SUBTOTAL/AGGREGATE
                       6 = ignore errors & nested SUBTOTAL/AGGREGATE
                       7 = ignore hidden rows, errors, nested SUBTOTAL/AGGREGATE
        array        : iterable (list / numpy array / pandas Series) of values (numbers or np.nan for errors)
        k            : optional numeric, used by LARGE(14), SMALL(15), PERCENTILE/QUARTILE (16-19)
        hidden       : optional boolean mask (same length as array). True = hidden row
        is_subtotal  : optional boolean mask (same length as array). True = value produced by SUBTOTAL/AGGREGATE

    Notes:
        - Values that represent "errors" should be np.nan (or produced as np.nan).
        - If options does NOT include 'ignore errors' and any np.nan remains, the function raises ValueError("#VALUE! 🚫 encountered error in data")
        - For exact SUBTOTAL/AGGREGATE ignoring: pass `is_subtotal` mask marking those positions.
        - For QUARTILE/PERCENTILE, `k` semantics:
            * For PERCENTILE.INC (16) and PERCENTILE.EXC (18): k should be between 0..1 (fraction)
            * For QUARTILE.INC (17) and QUARTILE.EXC (19): k should be 0..4 (quart index)
    
    *Example*:

     data = [82, 88, 91, 37, 56, 74, 82, 44, 95, 99, 70, 63, 56, 72, 84, 65, 88, 42, 77]

     print("Average =", AGGREGATE(1, 6, data))                      # 71.84210526315789
     print("Count =", AGGREGATE(2, 6, data))                        # 19
     print("CountA =", AGGREGATE(3, 6, data))                       # 19
     print("Max =", AGGREGATE(4, 6, data))                          # 99
     print("Min =", AGGREGATE(5, 6, data))                          # 37
     print("Product =", AGGREGATE(6, 6, data))                      # 9.439721027123594e+34
     print("Sum =", AGGREGATE(9, 6, data))                          # 1365
     print("Median =", AGGREGATE(10, 6, data))                      # 336.5847953216374
     print("Large(1) =", AGGREGATE(14, 6, data, 1))                 # 99
     print("Small(1) =", AGGREGATE(15, 6, data, 1))                 # 37
     print("Stdev.S =", AGGREGATE(7, 6, data))                      # 18.346247445230794
     print("Stdev.P =", AGGREGATE(8, 6, data))                      # 17.856925997891764
     print("Var.S =", AGGREGATE(11, 6, data))                       # 318.8698060941828
     print("Var.P =", AGGREGATE(12, 6, data))                       # 74
     print("Mode =", AGGREGATE(13, 6, data))                        # 56
     print("Percentile Inc (0.5) =", AGGREGATE(16, 6, data, 0.5))   # 74
     print("Quartile Inc (1) =", AGGREGATE(17, 6, data, 1))         # 59.5
     print("Percentile Exc (0.55) =", AGGREGATE(18, 6, data, 0.55)) # 77
     print("Quartile Exc (1) =", AGGREGATE(19, 6, data, 1))         # 56
    """
    if not isinstance(function_num, int) or not (1 <= function_num <= 19): raise ValueError("#VALUE! 🚫 function_num must be integer 1..19")
    if not isinstance(options, int) or not (0 <= options <= 7): raise ValueError("#VALUE! 🚫 options must be integer 0..7")
    s = pd.Series(array).reset_index(drop=True)
    n = len(s)
    def _validate_mask(name, mask):
        if mask is None: return pd.Series([False]*n)
        mask_s = pd.Series(mask).reset_index(drop=True)
        if len(mask_s) != n: raise ValueError(f"#VALUE! 🚫 {name} mask length must equal array length")
        return mask_s.astype(bool)
    hidden_mask = _validate_mask("hidden", hidden)
    subtotal_mask = _validate_mask("is_subtotal", is_subtotal)
    ignore_hidden = options in (1,3,5,7)
    ignore_errors = options in (2,3,6,7)
    ignore_subtotals = options in (4,5,6,7)
    coerced = pd.to_numeric(s, errors='coerce')  
    s = coerced
    keep_mask = pd.Series([True]*n)
    if ignore_hidden: keep_mask &= ~hidden_mask
    if ignore_subtotals: keep_mask &= ~subtotal_mask
    if ignore_errors: keep_mask &= ~s.isna()
    data = s[keep_mask].to_numpy(dtype=float)
    eff_mask = pd.Series([True]*n)
    if ignore_hidden: eff_mask &= ~hidden_mask
    if ignore_subtotals: eff_mask &= ~subtotal_mask
    eff_data = s[eff_mask]
    if (not ignore_errors) and eff_data.isna().any(): raise ValueError("#VALUE! 🚫 error value in array (set options to ignore errors)")
    if data.size == 0:
        if function_num in (2,3,9): return 0
        if function_num == 6: return 1 
        raise ValueError("#DIV/0! 🚫 no data to aggregate after applying options")
    def _nanmean(x): return np.nanmean(x)
    def _count(x): return int(np.count_nonzero(~np.isnan(x)))
    def _counta(x): return int(np.count_nonzero(~pd.isnull(x)))
    def _nanmax(x): return np.nanmax(x)
    def _nanmin(x): return np.nanmin(x)
    def _nanprod(x): return float(np.prod(x)) 
    def _stdev_s(x): return float(np.nanstd(x, ddof=1))
    def _stdev_p(x): return float(np.nanstd(x, ddof=0))
    def _var_s(x): return float(np.nanvar(x, ddof=1))
    def _var_p(x): return float(np.nanvar(x, ddof=0))
    def _median(x): return float(np.nanmedian(x))
    def _mode(x):
        sr = pd.Series(x).dropna()
        if sr.empty: raise ValueError("#N/A! 🚫 no mode")
        modes = sr.mode()
        if modes.empty: raise ValueError("#N/A! 🚫 no mode")
        return float(modes.iloc[0])
    def _large(x, kk):
        arr = np.sort(x)[~np.isnan(np.sort(x))]
        if kk is None: raise ValueError("#VALUE! 🚫 k is required for LARGE")
        kk = int(kk)
        if kk < 1 or kk > arr.size: raise ValueError("#NUM! 🚫 k out of range for LARGE")
        return float(arr[::-1][kk-1])
    def _small(x, kk):
        arr = np.sort(x)[~np.isnan(np.sort(x))]
        if kk is None: raise ValueError("#VALUE! 🚫 k is required for SMALL")
        kk = int(kk)
        if kk < 1 or kk > arr.size: raise ValueError("#NUM! 🚫 k out of range for SMALL")
        return float(arr[kk-1])
    def _percentile_inc(x, p):
        if p is None: raise ValueError("#VALUE! 🚫 k is required for PERCENTILE.INC (fraction 0..1)")
        p = float(p)
        if not (0 <= p <= 1): raise ValueError("#NUM! 🚫 p must be between 0 and 1 for PERCENTILE.INC")
        arr = np.sort(x[~np.isnan(x)])
        if arr.size == 0: raise ValueError("#DIV/0! 🚫 no data")
        n = arr.size
        if p == 0: return float(arr[0])
        if p == 1: return float(arr[-1])
        rank = 1 + (n - 1) * p
        lower = int(np.floor(rank)) - 1
        upper = int(np.ceil(rank)) - 1
        if lower == upper: return float(arr[lower])
        frac = rank - (lower + 1)
        return float(arr[lower] + frac * (arr[upper] - arr[lower]))
    def _quartile_inc(x, q):
        if q is None: raise ValueError("#VALUE! 🚫 k is required for QUARTILE.INC (0..4)")
        q = int(q)
        if not (0 <= q <= 4): raise ValueError("#NUM! 🚫 quart must be 0..4")
        if q == 0: return _percentile_inc(x, 0.0)
        if q == 4: return _percentile_inc(x, 1.0)
        return _percentile_inc(x, q/4.0)
    def _percentile_exc(x, p):
        if p is None: raise ValueError("#VALUE! 🚫 k is required for PERCENTILE.EXC (fraction 0..1 exclusive)")
        p = float(p)
        n = np.count_nonzero(~np.isnan(x))
        if n < 3: raise ValueError("#NUM! 🚫 PERCENTILE.EXC requires at least 3 data points")
        if not (0 < p < 1): raise ValueError("#NUM! 🚫 p must be between 0 and 1 (exclusive) for PERCENTILE.EXC")
        rank = p * (n + 1)
        if rank <= 1 or rank >= n: raise ValueError("#NUM! 🚫 p out of range for PERCENTILE.EXC")
        arr = np.sort(x[~np.isnan(x)])
        lower = int(np.floor(rank)) - 1
        upper = int(np.ceil(rank)) - 1
        if lower == upper: return float(arr[lower])
        frac = rank - (lower + 1)
        return float(arr[lower] + frac * (arr[upper] - arr[lower]))
    def _quartile_exc(x, q):
        if q is None: raise ValueError("#VALUE! 🚫 k is required for QUARTILE.EXC (0..4)")
        q = int(q)
        if not (0 <= q <= 4): raise ValueError("#NUM! 🚫 quart must be 0..4")
        if q == 0: return _percentile_exc(x, 0.0)  # Excel may error here; keep consistent
        if q == 4: return _percentile_exc(x, 1.0)
        return _percentile_exc(x, q/4.0)

    fm = {
        1: lambda x, kk=None: _nanmean(x),
        2: lambda x, kk=None: _count(x),
        3: lambda x, kk=None: _counta(x),
        4: lambda x, kk=None: _nanmax(x),
        5: lambda x, kk=None: _nanmin(x),
        6: lambda x, kk=None: _nanprod(x),
        7: lambda x, kk=None: _stdev_s(x),
        8: lambda x, kk=None: _stdev_p(x),
        9: lambda x, kk=None: float(np.nansum(x)),
        10: lambda x, kk=None: _var_s(x),
        11: lambda x, kk=None: _var_p(x),
        12: lambda x, kk=None: _median(x),
        13: lambda x, kk=None: _mode(x),
        14: lambda x, kk=None: _large(x, kk),
        15: lambda x, kk=None: _small(x, kk),
        16: lambda x, kk=None: _percentile_inc(x, kk),
        17: lambda x, kk=None: _quartile_inc(x, kk),
        18: lambda x, kk=None: _percentile_exc(x, kk),
        19: lambda x, kk=None: _quartile_exc(x, kk), }

    func = fm.get(function_num)
    if func is None: raise ValueError("#VALUE! 🚫 unsupported function_num")
    result = func(data, k)
    if isinstance(result, (np.floating, np.float64, np.float32)): return float(result)
    if isinstance(result, (np.integer, np.int64, np.int32)): return int(result)
    return result

def AMORLINC(cost: float, date_purchased: str, first_period: str, salvage: float, period: int, rate: float, basis: int = 1) -> float:
    """
    `=AMORLINC(cost, date_purchased, first_period, salvage, period, rate, [basis])` Returns the **linear depreciation** for each accounting period using the French accounting system.
    This method calculates depreciation linearly, prorated if needed for the first period.

    Parameters:
        cost (float): Initial cost of the asset
        date_purchased (str): Date of purchase (format: 'DD-MM-YYYY')
        first_period (str): End of first accounting period (format: 'DD-MM-YYYY')
        salvage (float): Salvage value at the end of asset life
        period (int): The depreciation period number (0 for first, 1 for second...)
        rate (float): Depreciation rate (e.g., 0.15 for 15%)
        basis (int, optional): Day count basis (default = 1):
            0 = 30/360 US
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = 30/360 European

    Example Inputs:

     print(AMORLINC(10000,"01-01-2020","31-12-2020",1000,2,0.2)) # -> 2000.0
    `Returns: float: Depreciation amount for the specified period`
    """
    try:
        purchase_date = pd.to_datetime(date_purchased, dayfirst=True)
        period_end = pd.to_datetime(first_period, dayfirst=True)
    except: raise ValueError("🚫 Invalid date format. Use 'DD-MM-YYYY'.")

    if salvage >= cost: raise ValueError("🚫 Salvage value must be less than cost.")
    if rate <= 0: raise ValueError("🚫 Rate must be a positive value.")

    if basis == 0 or basis == 4:
        d1 = purchase_date; d2 = period_end
        days_in_first = ((d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (d2.day - d1.day))
        year_basis = 360
    elif basis == 1: days_in_first = (period_end - purchase_date).days; year_basis = 366 if purchase_date.is_leap_year or period_end.is_leap_year else 365
    elif basis == 2: days_in_first = (period_end - purchase_date).days; year_basis = 360
    elif basis == 3: days_in_first = (period_end - purchase_date).days; year_basis = 365
    else: raise ValueError("🚫 Basis must be an integer between 0 and 4.")

    depreciation = 0.0
    for i in range(period + 1):
        if i == 0: depreciation = cost * rate * (days_in_first / year_basis)
        else:
            remaining = cost - (cost * rate * (days_in_first / year_basis)) - ((i - 1) * cost * rate)
            if remaining <= salvage: return 0.0
            depreciation = cost * rate
    return depreciation

def AND(*args) -> bool:
    """ 
    `=AND(logical1, [logical2], [logicaln])` Check whether all the arguments are **TRUE**, and returns **TRUE**, if all the arguments are **TRUE**, else return **FALSE**.

    *Example Inputs*:

     print(AND(True, 1, " "))          # -> True
     print(AND(2>=7))                  # -> False
     print(AND(True, 1, 3.14))         # -> True
     print(AND(True, 0, ""))           # -> False
     print(AND(True, None))            # -> True
     print(AND())                      # -> False
    """
    found_valid = False
    for val in args:
        if val is None or (isinstance(val, str) and val.strip() == ''): continue
        found_valid = True
        if isinstance(val, bool):
            if not val: return False
        elif isinstance(val, (int, float)):
            if val == 0: return False
        elif isinstance(val, str): 
            return False  
        else: return False  
    return True if found_valid else False

def ARABIC(input: str) -> int:
    """
    `=ARABIC(text)` Converts a **Roman** Numeral to **Arabic**.

    *Example Inputs*:

     print(ARABIC("XIV"))     # -> 14
     print(ARABIC("MMXXIV"))  # -> 2024
     print(ARABIC("IIII"))    # -> "#VALUE!"
     print(ARABIC("XYZ"))     # -> "#VALUE!"
    """
    roman_numerals = { 'M': 1000, 'CM': 900, 'D': 500, 'CD': 400,
                       'C': 100, 'XC': 90, 'L': 50, 'XL': 40,
                       'X': 10, 'IX': 9, 'V': 5, 'IV': 4, 'I': 1 }
    if not isinstance(input, str): raise ValueError("🚫 #VALUE!") 
    input = input.upper()

    i = 0; result = 0
    valid_roman = ""
    def int_to_roman(n):
        val_map = list(roman_numerals.items()); res = ""
        for roman, val in val_map:
            while n >= val:
                res += roman
                n -= val
        return res
    while i < len(input):
        if i + 1 < len(input) and input[i:i+2] in roman_numerals:
            result += roman_numerals[input[i:i+2]]
            valid_roman += input[i:i+2]
            i += 2
        elif input[i] in roman_numerals:
            result += roman_numerals[input[i]]
            valid_roman += input[i]
            i += 1
        else: raise ValueError("🚫 #VALUE!")
    if int_to_roman(result) != valid_roman: raise ValueError("#VALUE!") 
    return result

def AREAS(*args) -> int:
    total = 0
    for arg in args:
        if isinstance(arg, pd.DataFrame): total += len(arg.columns)
        elif isinstance(arg, pd.Series): total += 1
        elif isinstance(arg, str):
            cleaned = arg.replace(" ", "")
            refs = cleaned.split(",")
            total += len(refs)
        else: raise ValueError("🚫 #VALUE!") 
    return total

def ARRAYTOTEXT(array, format=0) -> str:
    """
    `=ARRAYTOTEXT(array, [format])` Returns a **text** representation of an **array**.
    
    Parameters:
        array: Enter a list or an array
        format: Decides Consice or Strict
        0 -> Enclosed with **Square**, seperated with **Commas**
        1 -> Enclosed with **Curly Brace**, seperated with **semi-colon**
    
    *Example Inputs*:

     ARRAYTOTEXT(["apple", "banana", "cherry"])             # "apple","banana","cherry"
     ARRAYTOTEXT(["apple", "banana", "cherry"], format=1)   # {"apple";"banana";"cherry"}
     ARRAYTOTEXT([[1, 2], True, False], format=0)           # "1,2","1","0"
     ARRAYTOTEXT([[1, 2], [3, 4], None], format=1)          # {"1,2";"3,4";""}
     ARRAYTOTEXT(pd.Series(["X", "Y", "Z"]), format=True)  # {"X";"Y";"Z"}
     ARRAYTOTEXT(np.array(["A", "B", "C"]), format=False)    # "A","B","C" 

    """
    rows = []
    def to_excel_val(val):
        if val is None: return "" if format == 0 else '""'
        if isinstance(val, bool): return "1" if format == 0 and val else ("0" if format == 0 else ('"1"' if val else '"0"'))
        if isinstance(val, (int, float)): return str(val) if format == 0 else f'"{val}"'
        return str(val) if format == 0 else f'"{val}"'

    if not isinstance(array, (list, tuple)): array = [[array]]
    elif all(not isinstance(row, (list, tuple)) for row in array): array = [array]

    for row in array:
        if not isinstance(row, (list, tuple)): row = [row]
        if format == 0: rows.append(f'"{",".join(to_excel_val(x) for x in row)}"')
        else: rows.append(";".join(to_excel_val(x) for x in row)) 

    if format == 0: return "[" + ",".join(rows) + "]"
    elif format==1: return "{" + ";".join(rows) + "}"
    else: raise ValueError("#VALUE!")

def ASIN(*args: int | float | str) -> float:
    """
    **=ASIN(number)** Returns the arcsine (inverse sine) of a number, in radians, in the range of -pi/2 to pi/2.

    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ASIN(0)            # -> 0.0
     ASIN("1")          # -> 1.5707963268
     ASIN(-1)           # -> -1.5707963268
     ASIN("0.4+0.1")    # -> 0.5235987756
     ASIN(0.5+0.3)      # -> 0.927295218
    """
    try:
        assert args, "Value Error: 🚫 ASIN() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ASIN() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ASIN expects a numeric value or a math-like string. Got `{arg}`")
            if number < -1 or number > 1: raise ValueError("Range Error: 🚫 Input must be between -1 to 1 (inclusive).")
            return np.arcsin(number)
    except AssertionError as ae: raise ValueError(str(ae))

def ASINH(*args: int | float | str) -> float:
    """
    **=ASINH(number)** Returns the inverse hyperbolic sine of a number.

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ASINH(0)           # -> 0.0
     ASINH("1")         # -> 0.881373587
     ASINH(-1)          # -> -0.881373587
     ASINH("2 + 3")     # -> 2.3124383413
     ASINH(-5)          # -> -2.3124383413
    """
    try:
        assert args, "Value Error: 🚫 ASINH() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ASINH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ASINH expects a numeric value or a math-like string. Got `{arg}`")
            return np.arcsinh(number)
    except AssertionError as ae: raise ValueError(str(ae))

def ATAN(*args: int | float | str) -> float:
    """
    **=ATAN(number)** Returns the arctangent (inverse tangent) of a number, in radians, in the range of -pi/2 to pi/2.

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ATAN(0)            # -> 0.0
     ATAN("1")          # -> 0.7853981634
     ATAN(-1)           # -> -0.7853981634
     ATAN("1/3")        # -> 0.3217505544
     ATAN(5 - 2)        # -> 1.2490457724
    """
    try:
        assert args, "Value Error: 🚫 ATAN() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ATAN() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ATAN expects a numeric value or a math-like string. Got `{arg}`")
            return np.arctan(number)
    except AssertionError as ae: raise ValueError(str(ae))

def ATAN2(*args: int | float | str) -> float:
    """
    **=ATAN2(x, y)** Returns the arctangent of the two numbers `x` and `y` (the angle from the X-axis to a point).

    `Parameters: Two # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ATAN2(1, 1)          # -> 0.7853981634
     ATAN2(0, 1)          # -> 0.0
     ATAN2(1, 0)          # -> 1.5707963268
     ATAN2(-1, -1)        # -> -2.3561944902
     ATAN2("3", "4")      # -> 0.643501109
    """
    try:
        assert args, "Value Error: 🚫 ATAN2() requires two numeric inputs."
        if len(args) != 2: raise ValueError("Parameters Error: 🚫 ATAN2() requires exactly two inputs.")
        processed = []
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: processed.append(float(arg))
            except: raise TypeError(f"Type Error: 🚫 ATAN2 expects numeric values or math-like strings. Got `{arg}`")
        return np.arctan2(processed[0], processed[1])
    except AssertionError as ae: raise ValueError(str(ae))

def ATANH(*args: int | float | str) -> float:
    """
    **=ATANH(number)** Returns the inverse hyperbolic tangent of a number. Input must be between -1 and 1 (exclusive).

    `Parameters: Only one # -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ATANH(0)            # -> 0.0
     ATANH(0.5)          # -> 0.5493061443
     ATANH(-0.5)         # -> -0.5493061443
     ATANH("0.8")        # -> 1.0986122887
     ATANH("-0.9")       # -> -1.4722194896
    """
    try:
        assert args, "Value Error: 🚫 ATANH() requires one numeric input."
        if len(args) != 1: raise ValueError("Parameters Error: 🚫 ATANH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ATANH expects a numeric value or a math-like string. Got `{arg}`")
            if number <= -1 or number >= 1: raise ValueError("Range Error: 🚫 Input must be greater than -1 and less than 1.")
            return np.arctanh(number)
    except AssertionError as ae: raise ValueError(str(ae))

def AVEDEV(*args) -> float:
    """
    `=AVEDEV(num_1, [num_2] ...)`
    
    Returns the **average of the absolute deviations** of data points from their mean.
    Accepts numbers, booleans, arrays, and numeric strings.
    
    *`Parameters: Multiple -> Number (but accepts arithmetics too) int | float | bool | str`*
    
    *Example Inputs*:
    
     print(AVEDEV([1, 2, 3, 4, 5]))                # 1.2
     print(AVEDEV(True, False))                    # 0.5
     print(AVEDEV("2+3", "4"))                     # 0.5
     print(AVEDEV([2*5, "12"], 14, "TRUE"))        # 4.125
     print(AVEDEV("apple", "banana"))              # 🚫 #DIV/0!
    """
    values = []
    def extract_numbers(item):
        if isinstance(item, (list, tuple)):
            for sub in item:
                extract_numbers(sub)
        elif isinstance(item, bool): values.append(1 if item else 0)
        elif isinstance(item, (int, float)): values.append(item)

        elif isinstance(item, str):
            s = item.strip()
            if not s: return
            if s.lower() == "true": values.append(1)
            elif s.lower() == "false": values.append(0)
            else:
                try: values.append(float(s))
                except ValueError: pass
        elif item is None: pass

    for arg in args: extract_numbers(arg)
    if not values: raise ValueError("🚫 #DIV/0!")

    arr = np.array(values, dtype=float)
    mean_val = np.mean(arr)
    abs_dev = np.abs(arr - mean_val)
    return np.mean(abs_dev)

def AVERAGE(*args) -> float:
    """
    `=AVERAGE(num_1, [num_2] ...)`
    
    Returns the average **(arithmetic mean)** of its arguments, which can be a number or names or array, or references that contains number.
    
    *`Parameters: Multiple -> Number (but accepts arithmetics too) int | float | str`*

    *Example Inputs*:

     print(AVERAGE(1, 2, 3))                         # 2.0
     print(AVERAGE([1.5, True, False, "apple"]))     # 1.5
     print(AVERAGE("TRUE", "FALSE", "None"))         # 0.5
     print(AVERAGE(22/7, "", None, [3.14, 7]))       # 4.427619047619047
     print(AVERAGE("apple", "banana"))               # #DIV/0!
     print(AVERAGE([1, 2], (3, 4), "5"))             # 3
    """
    values = []
    def extract_numbers(item):
        if isinstance(item, (list, tuple)):
            for sub in item:
                extract_numbers(sub)
        elif isinstance(item, bool): values.append(1 if item else 0)
        elif isinstance(item, (int, float)): values.append(item)

        elif isinstance(item, str):
            s = item.strip()
            if not s:  return
            if s.lower() == "true": values.append(1)
            elif s.lower() == "false": values.append(0)
            else:
                try: values.append(float(s))
                except ValueError: pass 
        elif item is None: pass
    for arg in args: extract_numbers(arg)
    if not values: raise ValueError("🚫 #DIV/0!")
    return sum(values) / len(values)

def AVERAGEA(*values) -> float:
    """
    `=AVERAGEA(val_1, [val_2] ...)`

    Returns the average **(arithmetic mean)** of its arguments, evaluating texts and FALSE in arguments as 0; TRUE evaluates as 1, Arguments can be a number or names or array, or references that contains number.
    
    *`Parameters: Multiple -> Number (but accepts arithmetics too) int | float | str`*
    
    *Example Inputs*:

     print(AVERAGEA(10, 10*2, "text", True, False))       # (10 + 20 + 0 + 1 + 0) / 5 = 6.2
     print(AVERAGEA([1, 2, "abc", True], False, None))    # (1 + 2 + 0 + 1 + 0) / 5 = 0.8
     print(AVERAGEA("apple", "banana"))                   # (0 + 0) / 2 = 0.0
    """
    processed = []
    for v in values:
        if isinstance(v, (list, tuple, np.ndarray)): processed.extend(v)
        else: processed.append(v)

    converted = []
    for v in processed:
        if isinstance(v, bool): converted.append(1 if v else 0)
        elif isinstance(v, (int, float)) and not isinstance(v, bool): converted.append(v)     
        elif v is None: continue
        else: converted.append(0)

    if len(converted) == 0: return np.nan
    return np.mean(converted)

def AVERAGEIF(range_vals, criteria, average_range=None) -> float:
    """
    `=AVERAGEIF(range, criteria, [average_range])`
    Finds Average **(arithemetic mean)** for the cells specified by a given condition or criteria 

    Parameters:
        range :
            *The range of cells to evaluate with the criteria.*
        criteria :
            *The condition that determines which cells are averaged.*
            *Can be a number, expression (e.g., ">5"), or text (e.g., "Apple").*
        average_range (optional) :
            *The actual set of cells to average. If omitted, `range` is used.*

    *Example Inputs*:

     print(AVERAGEIF([10, 20, 30, 40], ">15"))                           # (20 + 30 + 40) / 3 = 30
     print(AVERAGEIF([5, 7, 9, 11], "<10", [50, 60, 70, 80]))            # (50 + 60 + 70) / 3 = 60
     print(AVERAGEIF(["Apple", "Orange", "Apple"], "Apple", [5, 6, 7]))  # (5 + 7) / 2 = 6
     print(AVERAGEIF([True, False, True], True, [10, 20, 30]))           # (10 + 30) / 2 = 20
     print(AVERAGEIF([1, 2, 3], ">5"))                                   # No match → NaN
    """
    range_vals = np.array(range_vals)
    if average_range is None: average_range = range_vals
    else: average_range = np.array(average_range)
    s = pd.Series(range_vals)
    if criteria.startswith((">", "<", "=")): mask = s.astype(float).apply(lambda v: eval(f"v{criteria}"))
    else: mask = s == criteria
    filtered = average_range[mask]
    return np.mean(filtered) if len(filtered) > 0 else np.nan

def AVERAGEIFS(average_range, *criteria_pairs) -> float:
    """
    `=AVERAGEIFS(average_range, criteria_range1, criteria1, [criteria_range2, criteria2] ...)`
    Finds Average **(arithemetic mean)** for the cells specified by a given set of condition or criteria.

    Parameters:
        average_range : 
            *The actual set of cells to average.*

        criteria_rangeN : array-like
            *The range of cells to evaluate against criteria 'N.*

        criteriaN : str | int | float
            *The condition that determines which cells are included. Can be a number, expression (e.g., ">5"), or text (e.g., "Apple").*

    *Example Inputs*:
     print(AVERAGEIFS([50, 60, 70, 80], [1, 2, 3, 4], ">1"))                       # (60 + 70 + 80) / 3 = 70
     print(AVERAGEIFS([50, 60, 70, 80], [1, 2, 3, 4], ">1", [5, 6, 7, 8], "<8"))   # (60 + 70) / 2 = 65
     print(AVERAGEIFS([5, 6, 7], ["A", "B", "A"], "A", [True, False, True], True)) # (5 + 7) / 2 = 6
     print(AVERAGEIFS([10, 20, 30, 40], [2, 4, 6, 8], ">3", [1, 2, 3, 4], "<4"))   # (20 + 30) / 2 = 25
     print(AVERAGEIFS([100, 200, 300], [True, True, False], True))                 # (100 + 200) / 2 = 150
    """
    average_range = np.array(average_range)
    mask = np.ones(len(average_range), dtype=bool)
    
    for i in range(0, len(criteria_pairs), 2):
        crit_range = np.array(criteria_pairs[i])
        criteria = criteria_pairs[i+1]
        mask &= pd.Series(crit_range).apply(lambda x: eval(f"x{criteria}" if criteria[0] in "<>=" else f"x=={repr(criteria)}"))
    filtered = average_range[mask]
    return np.mean(filtered) if len(filtered) > 0 else np.nan

#B
from scipy.special import iv, jv, kv, yv
from scipy.stats import binom, beta

def BAHTTEXT(number: int | float) -> str:
    """
    `=BAHTTEXT(number)` Converts a number to a text **(baht)**

    *Example Inputs*:
     
     print(BAHTTEXT(1234.56))  # หนึ่งพันสองร้อยสามสิบสี่บาทห้าสิบหกสตางค์
     print(BAHTTEXT(5000))     # ห้าพันบาทถ้วน
    """
    number = round(float(number), 2)
    thai_numbers = ['', 'หนึ่ง', 'สอง', 'สาม', 'สี่', 'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า']
    thai_positions = ['', 'สิบ', 'ร้อย', 'พัน', 'หมื่น', 'แสน', 'ล้าน']
    def num_to_thai_words(n):
        n = int(n)
        if n == 0: return 'ศูนย์'
        words = ''
        position = 0
        while n > 0:
            digit = n % 10
            if digit != 0:
                if position == 0 and digit == 1 and words != '': words = 'เอ็ด' + words
                elif position == 1 and digit == 2: words = 'ยี่' + thai_positions[position] + words
                elif position == 1 and digit == 1: words = thai_positions[position] + words
                else: words = thai_numbers[digit] + thai_positions[position] + words
            position += 1
            n //= 10
        return words
    baht = int(number)
    satang = int(round((number - baht) * 100))
    baht_words = num_to_thai_words(baht) + 'บาท'
    if satang == 0: satang_words = 'ถ้วน'
    else: satang_words = num_to_thai_words(satang) + 'สตางค์'
    return baht_words + satang_words

def BASE(number: int, radix: int, min_length: int = 0) -> str:
    """
    `=BASE(number, radix, [min_length])` Converts a *number* into a text representation with the given **radix** (base)
    
    Parameters:
        number: → integer in base 10
        target_base: → (2 to 36) just means the numbering system you want to convert to:
            2 = binary (only 0,1)
            8 = octal (0–7)
            10 = decimal (normal numbers 0–9)
            16 = hexadecimal (0–9, A–F)
            Up to 36 = can use digits 0–9 and letters A–Z as symbols.
        min_length: → optional zero-padding length for output.

    *Example Input*:

     print(BASE(255, 16))          # FF
     print(BASE(255, 2, 12))       # 000011111111
     print(BASE(-255, 16, 4))      # -00FF
     print(BASE(123456, 36))       # 2N9C

    `So higher radix more symbols available for writing numbers.`
    """
    if not (2 <= radix <= 36): raise ValueError("#VALUE! 🚫 Radix must be between 2 and 36")
    if number == 0: return "0".zfill(min_length)
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    is_negative = number < 0
    number = abs(number)
    result = ""
    while number > 0:
        result = digits[number % radix] + result
        number //= radix
    if is_negative: result = "-" + result
    if len(result.lstrip("-")) < min_length: result = ("-" if is_negative else "") + result.lstrip("-").zfill(min_length)
    return result

def BESSELI(x, n) -> float:
    """
    `=BESSELI(x, n)` Returns the modified Bessel function **In(x)**

    Parameters:
        x (float): The value at which to evaluate the function.
        n (int): The order of the Bessel function (must be >= 0).

    *Example Input*:

        BESSELI(5, 2)   # 17.505614966624236
        BESSELI(10, 0)  # 2815.7166284662544
        BESSELI(3, 1)   # 3.95337021740261
        BESSELI(1, 0)   # 1.2660658777520084
        BESSELI(0.5, 0) # 1.0634833707413236
        BESSELI(7, 3)   # 85.1754868428438
        BESSELI(20, 5)  # 23018392.213413667
        BESSELI(50, 2)  # 2.8164306402451954e+20

    `Returns (float) The calculated Bessel I_n(x) value.`
    """
    if n<0: raise ValueError("#VALUE! 🚫 'n' should be above or equal to zero !")
    else: return iv(n, x)

def BESSELJ(x, n) -> float:
    """
    `=BESSELJ(x, n)` Returns the Bessel function of first kind **jn(x)**.

    Parameters:
        x (float): The value at which to evaluate the function.
        n (int): The order of the Bessel function (must be >= 0).

    *Example Input*:

        BESSELJ(5, 2)   # 0.04656511627775229
        BESSELJ(10, 0)  # -0.24593576445134832
        BESSELJ(3, 1)   # 0.33905895852593626
        BESSELJ(1, 0)   # 0.7651976865579666
        BESSELJ(0.5, 0) # 0.938469807240813
        BESSELJ(7, 3)   # -0.16755558799533432
        BESSELJ(20, 5)  # 0.15116976798239493
        BESSELJ(50, 2)  # -0.05971280079425883
    """
    if n<0: raise ValueError("#VALUE! 🚫 'n' should be above or equal to zero !")
    else: return jv(n, x)

def BESSELK(x, n) -> float:
    """
    `=BESSELK(x, n)` Returns the Bessel function of first kind **kn(x)**.

    Parameters:
        x (float): The value at which to evaluate the function.
        n (int): The order of the Bessel function (must be >= 0).

    *Example Input*:

       BESSELK(5, 2)   # 0.00530894371222346
       BESSELK(10, 0)  # 1.778006231616765e-05
       BESSELK(3, 1)   # 0.040156431128194184
       BESSELK(1, 0)   # 0.42102443824070834
       BESSELK(0.5, 0) # 0.9244190712276656
       BESSELK(7, 3)   # 0.0007710751535668902
       BESSELK(20, 5)  # 1.0538660139974233e-09
       BESSELK(50, 2)  # 3.547931838858198e-23
    """    
    if n<0: raise ValueError("#VALUE! 🚫 'n' should be above or equal to zero !")
    else: return kv(n, x)

def BESSELY(x, n) -> float:
    """
    `=BESSELY(x, n)` Returns the Bessel function of first kind **Yn(x)**.

    Parameters:
        x (float): The value at which to evaluate the function.
        n (int): The order of the Bessel function (must be >= 0).

    *Example Input*:

     BESSELY(5, 2)    # 0.3676628826055246
     BESSELY(10, 0)   # 0.05567116728359934
     BESSELY(3, 1)    # 0.32467442479180014
     BESSELY(1, 0)    # 0.088256964215677
     BESSELY(0.5, 0)  # -0.44451873350670656
     BESSELY(7, 3)    # 0.26808060304231507
     BESSELY(20, 5)   # -0.10003576788953246
     BESSELY(50, 2)   # 0.09579316872759651
    """
    if n<0: raise ValueError("#VALUE! 🚫 'n' should be above or equal to zero !")
    else: return yv(n, x)

def BIN2DEC(num: int | float | str) -> int:
    """
    `=BIN2DEC(num)` Converts a binary number to decimal.
    
    *Example Inputs*:

     print(BIN2DEC("1010"))    # 10
     print(BIN2DEC(1010))      # 10
     print(BIN2DEC("   110 ")) # 6
     print(BIN2DEC("1021"))    # ValueError
     print(BIN2DEC(12.5))      # TypeError

    `Any other String or Numbers except 0 or 1 return Error !`
    """
    if not isinstance(num, (str, int)): raise TypeError(" #VALUE! 🚫 BIN2DEC accepts only int or str inputs.")
    if isinstance(num, int): num_str = str(num)
    else: num_str = num.strip()
    if not num_str.isdigit() or any(ch not in "01" for ch in num_str): raise ValueError("#VALUE! 🚫 Input must contain only binary digits (0 or 1).")
    return int(num_str, 2)

def BIN2HEX(num) -> str:
    """
    `=BIN2HEX(num)` Converts a binary number to hexadecimal.
    
    *Example usage*:

     print(BIN2HEX("1010"))    # 'A'
     print(BIN2HEX(1011))      # 'B'
     print(BIN2HEX(" 1111 "))  # 'F'

    `Any other String or Numbers except 0 or 1 return Error !`

    """
    if not isinstance(num, (int, str)): raise TypeError("#VALUE! 🚫 BIN2HEX accepts only int or str.")
    bin_str = str(num).strip()
    if not bin_str: raise ValueError("#VALUE! 🚫 Empty input is not a valid binary number.")
    if not all(ch in '01' for ch in bin_str): raise ValueError("#VALUE! 🚫 Binary number must contain only 0s and 1s.")
    decimal_value = int(bin_str, 2)
    hex_value = hex(decimal_value)[2:].upper()
    return hex_value

def BIN2OCT(num: int | float | str) -> int:
    """
    `=BIN2OCT(num)` Convert a binary number to its octal representation.
    
    *Example usage*:

     print(BIN2OCT("1010"))    # 12
     print(BIN2OCT(1011))      # 15
     print(BIN2OCT(" 1111 "))  # 70
     print(BIN2OCT(111))       # 7

    `Any other String or Numbers except 0 or 1 return Error !`
    """
    bin_str = str(num).strip()
    if not bin_str or any(ch not in "01" for ch in bin_str): raise ValueError("#VALUE! 🚫 Input must be a binary number containing only 0 and 1.")
    decimal_value = int(bin_str, 2)
    octal_str = format(decimal_value, "o")
    return octal_str

def BETA_DIST(x: float, alpha: float, beta_param: float, cumulative: bool, A:float=0, B:float=1) -> float:
    """
    `=BETA.DIST(x, alpha, beta, cumulative, [A], [B])` Returns the beta probability distribution function
    
    Parameters:
        x: Value at which to evaluate the function
        alpha: Shape parameter α > 0
        beta_param: Shape parameter β > 0
        cumulative: True for CDF, False for PDF
        A (optional): Lower bound of interval (default 0)
        B (optional): Upper bound of interval (default 1)
    
    *Example Input*:

     print(BETA_DIST(0.5, 2, 3, True))                 # 0.6875
     print(BETA_DIST(0.5, 2, 3, False))                # 1.5000000000000004
     print(BETA_DIST(7, 2, 3, True, A=0, B=10))        # 0.9163
     print(BETA_DIST(7, 2, 3, False, A=0, B=10))       # 0.07559999999999999   
    """
    if B <= A: raise ValueError("#VALUE! 🚫 B must be greater than A")
    if not (A <= x <= B): raise ValueError(f"#VALUE! 🚫 x must be between {A} and {B}")
    z = (x - A) / (B - A)
    if cumulative: return beta.cdf(z, alpha, beta_param)
    else: return beta.pdf(z, alpha, beta_param) / (B - A)  

def BETA_INV(probability: float, alpha: float, beta: float, A: float = 0, B: float = 1) -> float:
    """
    `=BETA.INV(probability, alpha, beta, [A], [B])` Returns the inverse of the beta cumulative distribution function for a specified probability.

    Parameters:
        probability: The probability (0 ≤ p ≤ 1)
        alpha: Shape parameter α > 0
        beta_param: Shape parameter β > 0
        A (optional): Lower bound of interval (default 0)
        B (optional): Upper bound of interval (default 1)

    **Example Input**:

        print(BETA_INV(0.5, 2, 3))               # 0.385727...
        print(BETA_INV(0.95, 2, 3))              # 0.773...
        print(BETA_INV(0.95, 2, 3, 0, 10))       # 7.732...

    """
    if B <= A: raise ValueError("#VALUE! 🚫 B must be greater than A")
    if not (0 <= probability <= 1): raise ValueError("#VALUE! 🚫 probability must be between 0 and 1")
    result = beta.ppf(probability, alpha, beta)
    return A + result * (B - A)

def BINOM_DIST(number_s: int, trials: int, probability_s: float, cumulative=True) -> float:
    """
    `=BINOM.DIST(number_s, trials, probability_s, is_cummulative)` Returns the individual term of binomial distribution.

    Parameters:
        x : number of successes
        n : number of trials
        p : probability of success (0 <= p <= 1)
        cumulative : True for cumulative distribution, False for pmf

    *Example usage*:

     print(BINOM_DIST(2, 10, 0.5, False))  # 0.04394531250000004
     print(BINOM_DIST(2, 10, 0.5, True))   # 0.0546875
    """
    if cumulative: return binom.cdf(number_s, trials, probability_s)
    else: return binom.pmf(number_s, trials, probability_s)

def BINOM_DIST_RANGE(trials: int, probability_s: float, num_s: int, num_s2: int = None) -> float:
    """
    `=BINOM.DIST.RANGE(trials, probability_s, num_s, [num_s2])` Returns the probability of a trial result falling between two thresholds.

    Parameters:
        trials       : Number of independent trials (n >= 0)
        probability_s: Probability of success on each trial (0 <= p <= 1)
        num_s        : Number of successes for lower bound
        num_s2       : (Optional) Upper bound of successes. If omitted, only P(X = num_s) is returned.

    **Example Inputs**:

         print(BINOM_DIST_RANGE(60, 0.75, 45))         # 0.11822800461154298
         print(BINOM_DIST_RANGE(60, 0.75, 45, 50))     # 0.5236297934718878
    """
    if not (0 <= probability_s <= 1): raise ValueError("#VALUE! 🚫 probability_s must be between 0 and 1")
    if trials < 0 or num_s < 0 or (num_s2 is not None and num_s2 < 0): raise ValueError("#VALUE! 🚫 trials and successes must be non-negative integers")
    if num_s > trials or (num_s2 is not None and num_s2 > trials): raise ValueError("#VALUE! 🚫 successes cannot exceed number of trials")
    if num_s2 is not None and num_s2 < num_s: raise ValueError("#VALUE! 🚫 2nd number must be greater than or equal to First Number")
    if num_s2 is None: return binom.pmf(num_s, trials, probability_s)
    else: return binom.cdf(num_s2, trials, probability_s) - binom.cdf(num_s - 1, trials, probability_s)

def BINOM_INV(trials: int, probability_s: float, alpha: float) -> int:
    """
    `=BINOM.INV(trials, probability_s, alpha)`
    Returns the smallest number of successes for which the cumulative binomial
    distribution is greater than or equal to alpha.

    Parameters:
        trials       : Number of independent trials (n >= 0)
        probability_s: Probability of success on each trial (0 <= p <= 1)
        alpha        : Cumulative probability threshold (0 <= alpha <= 1)

    *Example Input*:

         print(BINOM_INV(6, 0.5, 0.75))   # 4
         print(BINOM_INV(10, 0.3, 0.9))   # 5
    """
    if not (0 <= probability_s <= 1): raise ValueError("#VALUE! 🚫 probability_s must be between 0 and 1")
    if not (0 <= alpha <= 1): raise ValueError("#VALUE! 🚫 alpha must be between 0 and 1")
    if trials < 0: raise ValueError("#VALUE! 🚫 trials must be non-negative integer")
    return int(binom.ppf(alpha, trials, probability_s))

def BITAND(number1: int, number2: int) -> int:
    """
    `=BITAND(number1, number2)` Returns a **bitwise** AND of two numbers.

    *Example Input*:

        print(BITAND(5, 3))    # 1  (0101 AND 0011 = 0001)
        print(BITAND(12, 25))  # 8  (1100 AND 11001 = 01000)
    """
    if number1 < 0 or number2 < 0: raise ValueError("#NUM! 🚫 numbers must be non-negative integers")
    if not (isinstance(number1, int) and isinstance(number2, int)): raise ValueError("#VALUE! 🚫 numbers must be integers")
    return number1 & number2

def BITOR(number1: int, number2: int) -> int:
    """
    `=BITOR(number1, number2)` Returns a **bitwise** OR of two numbers.

    *Example Input*:

        print(BITOR(5, 3))    # 7  (0101 OR 0011 = 0111)
        print(BITOR(12, 25))  # 29 (1100 OR 11001 = 11101)
    """
    if number1 < 0 or number2 < 0: raise ValueError("#NUM! 🚫 numbers must be non-negative integers")
    if not (isinstance(number1, int) and isinstance(number2, int)): raise ValueError("#VALUE! 🚫 numbers must be integers")
    return number1 | number2

def BITLSHIFT(number: int, shift_amount: int) -> int:
    """
    `=BITLSHIFT(number, shift_amount)` Returns a number **shifted left** by a given number of bits.

    *Example Input*:

        print(BITLSHIFT(5, 2))   # 20  (0101 << 2 = 10100)
        print(BITLSHIFT(12, 3))  # 96  (1100 << 3 = 1100000)
    """
    if number < 0 or shift_amount < 0: raise ValueError("#NUM! 🚫 numbers must be non-negative integers")
    if not (isinstance(number, int) and isinstance(shift_amount, int)): raise ValueError("#VALUE! 🚫 numbers must be integers")
    return number << shift_amount

def BITRSHIFT(number: int, shift_amount: int) -> int:
    """
    `=BITRSHIFT(number, shift_amount)` Returns a number **shifted right** by a given number of bits.

    *Example Input*:

        print(BITRSHIFT(20, 2))  # 5   (10100 >> 2 = 0101)
        print(BITRSHIFT(96, 3))  # 12  (1100000 >> 3 = 1100)
    """
    if number < 0 or shift_amount < 0: raise ValueError("#NUM! 🚫 numbers must be non-negative integers")
    if not (isinstance(number, int) and isinstance(shift_amount, int)): raise ValueError("#VALUE! 🚫 numbers must be integers")
    return number >> shift_amount

def BITXOR(number1: int, number2: int) -> int:
    """
    `=BITXOR(number1, number2)` Returns a **bitwise** XOR of two numbers.

    *Example Input*:

        print(BITXOR(5, 3))    # 6  (0101 XOR 0011 = 0110)
        print(BITXOR(12, 25))  # 21 (1100 XOR 11001 = 10101)
    """
    if number1 < 0 or number2 < 0: raise ValueError("#NUM! 🚫 numbers must be non-negative integers")
    if not (isinstance(number1, int) and isinstance(number2, int)): raise ValueError("#VALUE! 🚫 numbers must be integers")
    return number1 ^ number2

#C
from scipy import stats
from scipy.special import comb

def CEILING_MATH(number: int | float, significant: int | float = 1, mode: int = 0) -> float:
    """
    `=CEILING.MATH(number, [significant], [mode])`
    Rounds a number up, to the nearest integer or the nearest multiple of significance.

    Parameters:
        number : The number to round
        significant : Multiple to round to (default 1, must be > 0)
        mode : int — For negative numbers: 
                     0 = round away from zero (default)
                     nonzero = round toward zero

    *Example Input*:

        print(CEILING_MATH(4.3))             # 5
        print(CEILING_MATH(-4.3))            # -4
        print(CEILING_MATH(-4.3, 2))         # -4
        print(CEILING_MATH(-4.3, 2, 1))      # -2
        print(CEILING_MATH(4.3, 2))          # 6
        print(CEILING_MATH(4.3, 0.5))        # 4.5
    """
    if significant < 0: raise ValueError("#NUM! 🚫 significant must be positive")
    if significant == 0: return 0.0
    sign = np.sign(number) 
    return np.floor(number / significant) * significant if sign < 0 and mode != 0 else np.ceil(np.abs(number) / significant) * significant * sign

def CELL(info_type: str, reference) -> any:
    """
    `=CELL(info_type, reference)` Returns information about the formatting, location, or contents of the first cell, according to the sheet's reading order, in a reference .

    **Parameters**:
        **info_type**
            The type of cell information you want to retrieve **(case-insensitive)** :
                 "address"       → Returns the cell address as an absolute reference (e.g., "$B$2").
                 "column"        → Returns the column number of the reference (A=1, B=2, ...).
                 "contents"      → Returns the value/content of the reference cell.
                 "format"        → Returns a code representing the cell's number format ("G" for General, "A" for Alphanumeric).
                 "parentheses"   → Returns TRUE if the cell value is formatted with parentheses (negative values), FALSE otherwise.
                 "prefix"        → Returns the label prefix of the cell ("'", "\"", "^", or "") used for text alignment in Excel.
                 "protect"       → Returns TRUE if the cell is locked/protected (simulated TRUE).
                 "row"           → Returns the row number of the reference (1-based).
                 "type"          → Returns "b" if blank, "l" if label (text), "v" if value (number).
                 "width"         → Returns the approximate column width (simulated as length of string representation).

  

        **reference** : scalar value, NumPy array element, or Pandas cell. (The cell to retrieve information from)

    **Example Input**:

        df = pd.DataFrame({"A":[10, 20, np.nan], "B":["x", "y", "z"]})
        print(CELL("address", df.iloc[1,1]))        # "$B$2"
        print(CELL("column", df.iloc[1,1]))         # 2
        print(CELL("contents", df.iloc[1,1]))       # "y"
        print(CELL("format", df.iloc[0,0]))         # "G"
        print(CELL("parentheses", -50))             # True
        print(CELL("prefix", "Hello"))              # "'"
        print(CELL("protect", df.iloc[0,0]))        # True
        print(CELL("row", df.iloc[1,1]))            # 2
        print(CELL("type", df.iloc[0,0]))           # "v"
        print(CELL("width", df.iloc[0,0]))          # 2

    """
    info_type = info_type.lower()
    valid_info = {"address", "col", "contents", "format", "parentheses", "prefix", "protect", "row", "type", "width" }
    if info_type not in valid_info: raise ValueError("#VALUE! 🚫 Invalid info_type")
    if isinstance(reference, pd.Series):
        if len(reference) != 1: raise ValueError("#VALUE! 🚫 reference must be 1 cell")
        val = reference.iloc[0]; col_label = reference.name; row_label = reference.index[0]
    elif isinstance(reference, pd.DataFrame):
        if reference.shape != (1, 1): raise ValueError("#VALUE! 🚫 reference must be 1×1 DataFrame")
        val = reference.iat[0, 0]; col_label = reference.columns[0]; row_label = reference.index[0]
    else: val = reference; col_label = "A"; row_label = 1
    def col_letter(col):
        if isinstance(col, int): n = col
        elif isinstance(col, str) and col.isalpha(): return col.upper()
        else:
            try: n = int(col) + 1
            except: n = 1
        letters = ""
        while n > 0:
            n, rem = divmod(n - 1, 26)
            letters = chr(65 + rem) + letters
        return letters
    if info_type == "address": return f"${col_letter(col_label)}${row_label}"
    elif info_type == "col": return (ord(col_letter(col_label)[0]) - 64)
    elif info_type == "contents": return val
    elif info_type == "format":
        if isinstance(val, (int, float, np.number)): return "G"  # General
        elif isinstance(val, str): return "@"
        else: return "G"
    elif info_type == "parentheses": return 1 if isinstance(val, (int, float, np.number)) and val < 0 else 0
    elif info_type == "prefix":
        if isinstance(val, str):
            if val.startswith("'"): return "'"
            elif val.startswith('"'): return '"'
            else: return ""
        return ""
    elif info_type == "protect": return True
    elif info_type == "row": return row_label if isinstance(row_label, int) else 1
    elif info_type == "type":
        if val is None or (isinstance(val, float) and np.isnan(val)): return "b"
        elif isinstance(val, str): return "l"
        else: return "v"
    elif info_type == "width": return 8.43  
    raise ValueError("#VALUE! 🚫 Unsupported info_type")

def CHAR(number: int) -> str:
    """
    `=CHAR(number)` Returns the character specified by a number according to the ANSI/Unicode character set.

    **Example Input**:

        print(CHAR(65))    # "A"   → ANSI code 65 is uppercase A
        print(CHAR(97))    # "a"   → ANSI code 97 is lowercase a
        print(CHAR(48))    # "0"   → ANSI code 48 is digit zero
        print(CHAR(36))    # "$"   → ANSI code 36 is dollar sign
        print(CHAR(10))    # "\n"  → ANSI code 10 is line feed (newline)

    `**Parameters**: An integer between 1 and 255 representing the ANSI code of the desired character.`

    **Excel Notes**:
        - On Windows, `CHAR()` uses the ANSI character set (code page 1252 by default).
        - If you want to handle Unicode values above 255 in Excel, you must use `excelfred.UNICHAR()`.
    """
    if not isinstance(number, (int, np.integer)): raise ValueError("#VALUE! 🚫 number must be an integer")
    if number < 1 or number > 255: raise ValueError("#VALUE! 🚫 number must be between 1 and 255")
    return chr(number)

def CHISQ_DIST(x: float, deg_freedom: int, cumulative: bool) -> float:
    """
    `=CHISQ.DIST(x, deg_freedom, cumulative)` Returns the **left-tailed** probability of the **chi-squared** distribution.

    Parameters:
        x : float → Value at which to evaluate the distribution (must be ≥ 0).
        deg_freedom : int → Degrees of freedom (must be ≥ 1).
        cumulative : bool → TRUE for cumulative distribution (CDF), FALSE for probability density (PDF).

    *Example Input*:

         print(CHISQ_DIST(0.5, 1, True))    # 0.5204998778
         print(CHISQ_DIST(0.5, 1, False))   # 0.4393912895
         print(CHISQ_DIST(2, 2, True))      # 0.6321205588
         print(CHISQ_DIST(2, 2, False))     # 0.1839397206
         print(CHISQ_DIST(5, 10, True))     # 0.0954659664
    """
    if x < 0: raise ValueError("#NUM! 🚫 x must be non-negative")
    if deg_freedom < 1: raise ValueError("#NUM! 🚫 degrees of freedom must be ≥ 1")
    if cumulative: return stats.chi2.cdf(x, deg_freedom)
    else: return stats.chi2.pdf(x, deg_freedom)

def CHISQ_DIST_RT(x: float, deg_freedom: int) -> float:
    """
    `=CHISQ.DIST.RT(x, deg_freedom)` Returns the **right-tailed** probability of the **chi-squared** distribution.

    Parameters:
        x : float → Value at which to evaluate (must be ≥ 0).
        deg_freedom : int → Degrees of freedom (must be ≥ 1).

    *Example Input*:

         print(CHISQ_DIST_RT(0.5, 1))   # 0.4795001222
         print(CHISQ_DIST_RT(2, 2))     # 0.3678794412
         print(CHISQ_DIST_RT(5, 10))    # 0.9045340337
         print(CHISQ_DIST_RT(15, 20))   # 0.8282028557
         print(CHISQ_DIST_RT(30, 25))   # 0.2424253566
    """
    if x < 0: raise ValueError("#NUM! 🚫 x must be non-negative")
    if deg_freedom < 1: raise ValueError("#NUM! 🚫 degrees of freedom must be ≥ 1")
    return stats.chi2.sf(x, deg_freedom)

def CHISQ_INV(prob: float, deg_freedom: int) -> float:
    """
    `=CHISQ.INV(prob, deg_freedom)` Returns the **inverse** of the **left-tailed** probability of the chi-squared distribution.

    Parameters:
        prob : float → Probability (0 < prob < 1).
        deg_freedom : int → Degrees of freedom (must be ≥ 1).

    *Example Input*:

        print(CHISQ_INV(0.5204998778, 1))   # 0.49999999997030736
        print(CHISQ_INV(0.6321205588, 2))   # 1.9999999998447435
        print(CHISQ_INV(0.0954659664, 10))  # 4.793572111719336
        print(CHISQ_INV(0.5, 5))            # 4.351460191
        print(CHISQ_INV(0.9, 3))            # 6.251389
    """
    if not (0 < prob < 1): raise ValueError("#NUM! 🚫 prob must be between 0 and 1")
    if deg_freedom < 1: raise ValueError("#NUM! 🚫 degrees of freedom must be ≥ 1")
    return stats.chi2.ppf(prob, deg_freedom)

def CHISQ_INV_RT(prob: float, deg_freedom: int) -> float:
    """
    `=CHISQ.INV.RT(prob, deg_freedom)` Returns the **inverse** of the **right-tailed** probability of the chi-squared distribution.

    Parameters:
        prob : float → Probability (0 < prob < 1).
        deg_freedom : int → Degrees of freedom (must be ≥ 1).

    *Example Input*:

        print(CHISQ_INV_RT(0.4795001222, 1))  # 0.49999999997030786
        print(CHISQ_INV_RT(0.3678794412, 2))  # 1.9999999998447444
        print(CHISQ_INV_RT(0.9045340337, 10)) # 4.793572110121122
        print(CHISQ_INV_RT(0.5, 5))           # 4.351460191
        print(CHISQ_INV_RT(0.1, 3))           # 6.251389
    """
    if not (0 < prob < 1): raise ValueError("#NUM! 🚫 prob must be between 0 and 1")
    if deg_freedom < 1: raise ValueError("#NUM! 🚫 degrees of freedom must be ≥ 1")
    return stats.chi2.isf(prob, deg_freedom)

def CHISQ_TEST(test_range, expected_range) -> float:
    """
    `=CHISQ.TEST(test_range, expected_range)` Returns the test for independence from the chi-squared distribution.

    Parameters:
        test_range : array-like → Observed data.
        expected_range : array-like → Expected values.

    *Example Input*:

        observed = np.array([[10, 20, 30], [6,  9,  17]])
        expected = np.array([[8,  18, 34], [8, 11, 13]])
        print(CHISQ_TEST(observed, expected))  # 0.606
    """
    observed = np.array(test_range, dtype=float)
    expected = np.array(expected_range, dtype=float)
    if observed.shape != expected.shape: raise ValueError("#N/A 🚫 observed and expected ranges must have the same dimensions")
    chi_sq = ((observed - expected) ** 2 / expected).sum()
    df = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    return stats.chi2.sf(chi_sq, df)

def CHOOSE(index_num: int, *values: any) -> any:
    """
    `=CHOOSE(index_num, val1, [val2], ..., [valN])` Returns the value from a list of values based on the given index.

    Parameters:
        index_num :
            The position of the value to return. (1-based index, same as Excel)
        *values :
            One or more values among which to choose.

    Raises:
        ValueError: If index_num is not between 1 and len(values), or if index_num is not an integer.

    *Example Input*:

        print(CHOOSE(1, "Apple", "Banana", "Cherry"))   # Apple
        print(CHOOSE(3, 10, 20, 30, 40))                # 30
        print(CHOOSE(2, True, False))                   # False
        print(CHOOSE(4, "A", "B", "C", "D", "E"))       # D
        print(CHOOSE(1, 5.5, 6.6, 7.7))                 # 5.5
    """
    if not isinstance(index_num, (int, np.integer)): raise ValueError("#VALUE! 🚫 index_num must be an integer")
    if index_num == 0: raise TypeError("#NUM! 🚫 Index in CHOOSE starts from 1, Unlike usual array format")
    if index_num < 1 or index_num > len(values): raise ValueError("#VALUE! 🚫 index_num is out of range")
    return values[index_num - 1]

def CODE(text: str) -> int:
    """
    `=CODE(text)` Returns a numeric code for the first character of a text string.
    In Excel, this is based on **ANSI/Unicode** codes depending on version.

    *Example Input*:
    
        print(CODE("A"))       # 65   (ASCII for 'A')
        print(CODE("a"))       # 97   (ASCII for 'a')
        print(CODE("😀"))      # 128512 (Unicode for 😀)
        print(CODE("Excel"))   # 69   (ASCII for 'E')
        print(CODE("1"))       # 49   (ASCII for '1')

    `Parameters: The text string from which to return the code of the first character.`
    """
    if not isinstance(text, str): raise ValueError("#VALUE! 🚫 text must be a string")
    if text == "": raise ValueError("#VALUE! 🚫 text cannot be empty")
    return ord(text[0])

def COLUMN(reference: any) -> int | list:
    """
    `=COLUMN(reference)` Returns the **column number** of a reference

    *Example Inputs*:

     print("COLUMN('A') →", COLUMN('A'))                # 1
     print("COLUMN('AA') →", COLUMN('AA'))              # 27
     arr = np.array([[1, 2, 3], [4, 5, 6]])
     print("COLUMN(arr) →", COLUMN(arr))                # [1, 2, 3] 

     df = pd.DataFrame({ 'Name': ['Alice', 'Bob'],
     'Age': [25, 30], 'City': ['NY', 'LA'] })
     print("COLUMN(df) →", COLUMN(df))                  # [1, 2, 3]
     print("COLUMN(df['City']) →", COLUMN(df['City']))  # 3

    `Parameter - Accepts reference in dataframe, series, array, list formats `
    """
    if isinstance(reference, str):
        reference = reference.strip().upper()
        col_num = 0
        for char in reference:
            if not 'A' <= char <= 'Z': raise ValueError("#NUM! 🚫 Invalid column letter.")
            col_num = col_num * 26 + (ord(char) - ord('A') + 1)
        return col_num    
    if isinstance(reference, pd.Series):
        if reference.name is None: raise ValueError("#VALUE! 🚫 Series has no column name.")
        col_names = reference.to_frame().columns.tolist()
        return col_names.index(reference.name) + 1    
    if isinstance(reference, pd.DataFrame): return list(range(1, len(reference.columns) + 1))    
    if isinstance(reference, np.ndarray):
        if reference.ndim == 1: return 1 
        return list(range(1, reference.shape[1] + 1))
    raise TypeError("#REF! 🚫 Unsupported reference type.")

def COLUMNS(array: list | dict) -> int:
    """
    `=COLUMNS(array)` Returns the number of columns in an array or a reference

    *Example Inputs*:

     print("COLUMNS(df) =>", COLUMNS(pd.DataFrame({'A': [1,2,3],'B': [4,5,6], 'C': [7,8,9]})))  # 3
     print("COLUMNS(lst) =>", COLUMNS([[1,2],[3,4]]))                                           # 2
    
    `Parameter - Accepts reference in dataframe, series, array, list formats `
    """    
    if isinstance(array, pd.DataFrame): return array.shape[1]
    elif isinstance(array, pd.Series): return 1    
    elif isinstance(array, np.ndarray): return 1 if array.ndim == 1 else array.shape[1] 
    elif isinstance(array, list):
        if len(array) == 0: return 0
        elif isinstance(array[0], list): return len(array[0])
        else: return 1
    else: raise TypeError("#REF! 🚫 Unsupported type for COLUMNS function.")

def COMBIN(number: int, number_chosen: int) -> int:
    """
    `=COMBIN(number, number_chosen)` Returns the **number of combinations** for a given number of items.

    Parameters:
        number         → Total number of items (n)
        number_chosen  → Number of items to choose (k)

    *Example Inputs*:

         print(COMBIN(10, 2))    # 45
         print(COMBIN(5, 3))     # 10
         print(COMBIN(8, 0))     # 1
         print(COMBIN(6, 6))     # 1
         print(COMBIN(6, 1))     # 6
    """
    if not (isinstance(number, int) and isinstance(number_chosen, int)): raise ValueError("#VALUE! 🚫 Parameters must be integers.")
    if number < 0 or number_chosen < 0: raise ValueError("#NUM! 🚫 Parameters must be non-negative.")
    if number_chosen > number: raise ValueError("#NUM! 🚫 number_chosen cannot be greater than number.")
    return int(comb(number, number_chosen, exact=True))

def COMBINA(number: int, number_chosen: int) -> int:
    """
    `=COMBINA(number, number_chosen)` Returns the **number of combinations with repetitions** allowed.

    `Parameters`:
        number         → Total number of items (n)
        number_chosen  → Number of items to choose (k)

    *Example Inputs*:

         print(COMBINA(10, 2))    # 55
         print(COMBINA(5, 3))     # 35
         print(COMBINA(8, 0))     # 1
         print(COMBINA(6, 6))     # 462
         print(COMBINA(6, 1))     # 6
    """
    if not (isinstance(number, int) and isinstance(number_chosen, int)): raise ValueError("#VALUE! 🚫 Parameters must be integers.")
    if number <= 0 or number_chosen < 0: raise ValueError("#NUM! 🚫 number must be > 0 and number_chosen must be non-negative.")
    return int(comb(number + number_chosen - 1, number_chosen, exact=True))

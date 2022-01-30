any = "ANY"
args = ""
state = False


def activator(val):
    """
    It's a value that if activated returns TRUE
    """
    global state
    if val == True: state = True
    return state


def retrive_activator():
    """
    Retrieves activator's value
    """
    global state
    state_val, state = state, False
    return state_val


def args_check(fun, *kargs):
    """
    Parameters
    ----------
    fun : function
        The name of the function to which to pass the parameters
    kargs : strings
        Variable number of parameters, each one represents a parameter of the function
    """
    global args
    kargs = list(kargs)
    if len(args) == len(kargs):
        arguments_to_pass = []
        for i in range(0, len(kargs)):
            condition = (args[i] not in kargs[i]) if isinstance(kargs[i], list) else args[i] != kargs[i]
            if condition:
                if kargs[i] == "ANY":
                    arguments_to_pass.append(args[i])
                else:
                    activator(False)
                    return False
        activator(True)
        fun() if not arguments_to_pass else fun(*arguments_to_pass)
        return True

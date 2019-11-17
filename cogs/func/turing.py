import yaml
from time import sleep


class Tape:
    """
    Tape data structure for usage with the machines.
    """

    def __init__(self):
        self.content = {}

    @staticmethod
    def index_check(i):
        try:
            if not i >= 0:
                raise ValueError("Input must be greater or equal 0.")
        except TypeError:
            raise TypeError("Indices must be integers.")

    def get(self, i):
        self.index_check(i)
        return self.content.get(i)

    def set(self, i, v):
        self.index_check(i)
        self.content[i] = v

    def clear(self):
        self.content = {}


class OperableTuringMachine:
    """
    Implementation of a Turing Machine with a head that can be directly operated,
    intended as a core to a proper state transition based machine.
    """

    def __init__(self, blank="_", display_after_op=False, animate=False, animate_delay=0.5):
        self.tape = Tape()
        self.head = 0
        self.max = 0
        self.blank = blank
        self.display_after_op = display_after_op
        self.animate = animate
        self.animate_delay = animate_delay

    def display(self):
        if self.display_after_op:
            print(self)
            if self.animate:
                sleep(self.animate_delay)
                print('\r\r\r', end='')

    def __str__(self):
        result = "["
        head_delta = 1
        for i in range(self.max + 1):
            v = self.tape.get(i)

            if i < self.head:
                if v is not None:
                    head_delta += len(str(v)) + 1
                else:
                    head_delta += len(self.blank) + 1

            if i != 0:
                result += '|'

            if v is None:
                result += self.blank
            else:
                result += str(v)

        result += "]"
        result += "\n" + head_delta * " " + "^"
        return result

    """
    Load a string into the tape, must be a list of symbols.
    """
    def load_string(self, string):
        self.clear()
        if self.blank in string:
            raise ValueError("Blanks cannot be in input strings.")
        i = 0
        for symbol in string:
            self.tape.set(i, symbol)
            i += 1
        self.head = 0
        self.max = i - 1 if i > 0 else 0
        self.display()

    def clear(self):
        self.tape.clear()
        self.head = 0
        self.max = 0

    def left(self):
        if self.head != 0:
            self.head -= 1
        self.display()

    def right(self):
        self.head += 1
        if self.head > self.max:
            self.max = self.head
        self.display()

    def read(self):
        v = self.tape.get(self.head)
        if v is None:
            return self.blank
        else:
            return v

    def write(self, v):
        self.tape.set(self.head, v)
        self.display()


class TuringMachine:
    """
    Implementation of a properly controlled Turing machine by using
    OperableTuringMachine as an internal attribute.
    The states, alphabet, and tape alphabet of the machine are automatically
    inferred and validated.
    Arguments:
        transitions - a dict where keys are origin states, and values are an array of tuples of the form:
            (read in symbol, destination state, write out symbol, movement direction):
                read in - any relevant symbol
                destination - any relevant destination state
                write out - any relevant symbol
                movement - "l", "r", "left" or "right"
        state_state - a state mentioned as a from_state in some Transition that the machine start in
        accept_state, reject_state - states intended as the name implies
    """

    def __init__(self, transitions, start_state, accept_state, reject_state, step_limit=1000,
                 blank='_', display_after_op=False, animate=False, animate_delay=0.5):

        if not isinstance(transitions, dict):
            raise TypeError("transitions must be a dictionary")
        # need to validate that there aren't multiple routes for some symbol (earliest will be used anyway)
        self.transitions = transitions

        if start_state not in transitions:
            raise KeyError("start_state must be a key of transitions")
        self.start_state = start_state
        self.current_state = start_state

        self.accept_state = accept_state
        self.reject_state = reject_state

        self.M = OperableTuringMachine(blank, display_after_op, animate, animate_delay)
        self.frames = []
        self.step_limit = step_limit

    def _run_once(self):
        edges = self.transitions[self.current_state]
        symbol = self.M.read()

        for edge in edges:
            read_in, destination, write_out, movement = edge
            if symbol != read_in:
                continue

            self.M.write(write_out)
            if movement in ["l", "left"]:
                self.M.left()
            else:
                self.M.right()
            self.current_state = destination
            return True

        return False

    """
    Runs the machine on a string.

    Returns:
        -2: steps exceeded limit (probably looping)
        -1: halted (no transition for symbol)
        0: reached reject or stopping on non-accept state
        1: reached accept
    """
    def run(self, string):
        self.current_state = self.start_state
        self.M.load_string(string)

        self.frames = []
        steps = 0
        while 1:
            self.frames.append(str(self.M))
            ran = self._run_once()
            steps += 1
            if steps > self.step_limit:
                return -2
            if not ran:
                return -1
            if self.current_state == self.reject_state:
                return 0
            if self.current_state == self.accept_state:
                return 1

    def run_frames(self, string):
        return self.run(string), self.frames


def run_frames_serialised(encoding):
    blank = '_'

    try:
        data = yaml.safe_load(encoding)
    except yaml.YAMLError:
        raise SyntaxError("Invalid YAML received.")

    if "start" in data:
        start_state = data.pop("start")
    else:
        raise SyntaxError('No start state found. Specify one with "start: state_name"')

    input_data = data.pop("input", "")

    if blank in input_data:
        raise SyntaxError('The blank character "{}" cannot be in input data.'.format(blank))

    accept_state = data.pop("accept", None)
    reject_state = data.pop("reject", None)

    transitions = {}
    for key in data:
        edges = data[key]

        if type(edges) is not list:
            raise SyntaxError('Transitions from state not specified correctly.'
                              'Syntax: "start_state: [transition1, transition2, ...]"'
                              'where each transition is of the form [symbol, next_state, write, movement]')

        for edge in edges:
            if type(edge) is not list or len(edge) != 4:
                raise SyntaxError('Transition not specified correctly. Syntax: "[symbol, next_state, write, movement]"')

            movement = edge[3]

            if type(movement) is not str or movement.lower() not in ['l', 'r', 'left', 'right']:
                raise SyntaxError('Movement direction specified incorrectly. Use "l", "r", "left", or "right"')

        transitions[key] = tuple(edges)

    M = TuringMachine(transitions, start_state, accept_state, reject_state, 250, blank)
    return M.run_frames(input_data)

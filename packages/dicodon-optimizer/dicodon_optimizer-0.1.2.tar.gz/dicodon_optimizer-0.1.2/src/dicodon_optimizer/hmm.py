"""A tiny implementation of just enough Hidden-Markov-Model (hmm) algorithms
for our application.

This approach was chosen instead of a preexisting hmm library because most
of them were C based (and would not run on google app engine), or their
code quality was insufficient.

"""
import math


class DegenerateHMM:
    """
    A degenerate Hidden-Markov-Model:

    Each state has exactly one emission.

    The model can start in any state (to be precise:
    it can move from the (user-invisible) begin state to any other).
    Also, no enforcement of probability notions
    is in place, scores may be any positive value -
    they are multiplied to get final scores,
    and either a 0 or no entry means: there is no such transition.

    """

    def __init__(self, states, transition_scores):
        """Create a DegenerateHMM from a dict
        of @states = {statename: emission_symbol}
        and transition_scores,
        a dict of {(from_statename, to_statename): score}
        """
        self.states = states
        self.transition_scores = transition_scores
        self.allowed_emissions = set(self.states.values())
        for (from_state, to_state) in self.transition_scores:
            if not from_state in self.states:
                raise ValueError(
                    "There was a transition from %s to %s, but %s was not in 'states'"
                    % (from_state, to_state, from_state)
                )
            if not to_state in self.states:
                raise ValueError(
                    "There was a transition from %s to %s, but %s was not in 'states'"
                    % (from_state, to_state, to_state)
                )
        transformed_scores = {}
        for key in self.transition_scores:
            if self.transition_scores[key] > 0:
                transformed_scores[key] = math.log(self.transition_scores[key], 2)
            elif self.transition_scores[key] < 0:
                raise ValueError(
                    "Negative scores are not allowed (was in transition %s -> %s)" % key
                )
                # transformed_scores[key] = self.transition_scores[key]
        for from_state in self.states:
            for to_state in self.states:
                if not (from_state, to_state) in transformed_scores:
                    transformed_scores[from_state, to_state] = float("-inf")
        self.transition_scores = transformed_scores

    def viterbi(self, observed_sequence):
        """Given a list of observed emissions,
        give us the maximal score and path through the hidden markov model
        @observed_sequence: an iterable of symbols
        result: (maximum_score, [state_0, state_1, state_2..., state_len(observed_sequence)])

        Throws a ModelSequenceMismatchExecption if the observed_sequence can not
        have been produced by this model
        """
        if not observed_sequence:
            return 0, []

        V = (
            []
        )  # the score of the survivor path that ended in state y at observed_sequence t
        for t in range(0, len(observed_sequence)):
            if observed_sequence[t] not in self.allowed_emissions:
                raise ValueError("Invalid emission: %s" % observed_sequence[t])
            V.append({})
        path = (
            {}
        )  # for the position we have reached in observed_sequence, the survivor paths for each possible state

        # initialize for leaving the 'virtual' beginning state'
        # score is 0 for a valid transition,
        # so this 'virtual' begin state does not affect the final score
        for state, emission in self.states.items():
            V[0][state] = 0 if emission == observed_sequence[0] else float("-inf")
            path[state] = [state]

        for t in range(1, len(observed_sequence)):
            new_path = {}  # we only keep the survivor paths for the latest t

            any_survivors = (
                False  # to check if this HMM could have reached this state...
            )
            for (
                to_state,
                emission,
            ) in self.states.items():  # for each state we could potentially end up
                if (
                    emission == observed_sequence[t]
                ):  # this is valid transition, we can end up here
                    # let's find out what's the most likely state we could have come from
                    survivor_score = float("-inf")
                    survivor_state = None
                    for from_state, emission in self.states.items():
                        # how expensive is it to go from from_state to to_state?
                        transition_score = self.transition_scores[from_state, to_state]
                        # and how good was being in from_state in the first place
                        score_for_being_in_from_state = V[t - 1][from_state]
                        score_here = (
                            transition_score + score_for_being_in_from_state
                        )  # + in log is * in the normal scale
                        if (
                            score_here > survivor_score
                        ):  # it's best (so far) to have come from from_state!
                            survivor_score = score_here
                            survivor_state = from_state
                            any_survivors = (
                                True  # this Hmm can have produced this sequence
                            )
                    if (
                        survivor_state is not None
                    ):  # there is no way we can have ended up in to_state. But there might be other states with the right emission
                        new_path[to_state] = path[survivor_state] + [to_state]
                        V[t][to_state] = survivor_score
                    else:
                        V[t][to_state] = float("-inf")
                else:
                    # new_path[to_state] = None #no access to this path should happen. Not having this line would make it throw a KeyError if access did happen.
                    V[t][to_state] = float("-inf")

            if not any_survivors:
                raise ModelSequenceMismatchException(
                    "This HMM can't have generated this sequence in position %i" % t
                )
            path = new_path
        final_scores = V[-1]
        maximum_final_score = float("-inf")
        maximum_final_state = None
        for state in final_scores:
            if final_scores[state] > maximum_final_score:
                maximum_final_score = final_scores[state]
                maximum_final_state = state
        if maximum_final_state is None:
            raise ModelSequenceMismatchException(
                "This HMM can't have generated this sequence in position %i"
                % len(observed_sequence)
            )
        return pow(2, maximum_final_score), path[maximum_final_state]

    def score(self, state_sequence):
        """For list of states, calculate the score"""
        score = 0
        for t in range(1, len(state_sequence)):
            key = state_sequence[t - 1], state_sequence[t]
            score += self.transition_scores[key]
        if score == float("-inf"):
            raise ModelSequenceMismatchException()
        elif score == 0:  # and len(state_sequence) == 1
            return 0
        else:
            return pow(2, score)


class ModelSequenceMismatchException(Exception):
    """An exception thrown if an HMM is passed a sequence of emissions it could not have produced"""

    pass

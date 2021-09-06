#——————————————————————————————————————————————————————————————#
import heapq as hq
import os

# 定义了一个swap函数以替代c++中的swap
def pyswap(t1, t2):

    return t2, t1
# 定义了一个空State函数
class State(object):
    pass
class LoopNest():
    pass
class random_dropout():
    pass
#——————————————————————————————————————————————————————————————#
# A priority queue of states, sorted according to increasing
# cost. Never shrinks, to avoid reallocations.
# Can't use std::priority_queue because it doesn't support unique_ptr.
class StateQueue(object):

    def __init__(self):
        self.__storage = []
        self.__sz = 0

    class CompareStates(object):
        def functorMethod(self, a, b):
            return a.cost > b.cost


    def emplace(self,s):
        if self.__sz >= len(self.__storage):
            self.__storage.resize(max(self.__sz * 2, 64))
        if(self.__sz < len(self.__storage)) :
            print( self.__sz , " " , len(self.__storage) , "\n")
        self.__storage[self.__sz] = s #std::move是一个函数（函数模板），作用是将传入参数强制转换成右值
        self.__sz += 1
        hq.heappush(self.__storage, self.__sz)

    def pop(self):
        if(self.__sz <= len(self.__storage)):
            print(self.__sz , " " , len(self.__storage),"\n")
        hq.heappushpop(self.__storage, self.__sz)
        self.__sz -= 1
        return self.__storage[self.__sz]

    def top(self):
        return self.__storage[0]

    def empty(self):
        return self.__sz == 0

    def size(self):
        return self.__sz

    def swap(self, other):
        self.__storage.swap(other.__storage)
        pyswap(self.__sz, other.__sz)

    def get_item(self, idx):
        return self.__storage[idx]

    # 改写了resort函数
    def resort(self):
            h = []
            for value in self.__sz:
                hq.heappush(h, value)
            return [hq.heappop(h) for i in range(len(h))]


    def clear(self):
        i = 0
        while i < self.__sz:
            self.__storage[i] = State>({})
            i += 1
        self.__sz = 0


#——————————————————————————————————————————————————————————————#
# Configure a cost model to process a specific pipeline.

def configure_pipeline_features(self, dag, params, cost_model):
    cost_model.reset()
    cost_model.set_pipeline_features(dag, params)
#——————————————————————————————————————————————————————————————#

# A single pass of coarse-to-fine beam search.
def optimal_schedule_pass(self, dag, outputs, params, cost_model, rng, beam_size, memory_limit, pass_idx, num_passes, tick, permitted_hashes):

    if cost_model != None:
        configure_pipeline_features(dag, params, cost_model)

    q = StateQueue()
    pending = StateQueue()

    # The initial state, with no decisions made
    initial = State()
    initial.root = LoopNest()
    q.emplace(initial)

    expanded = 0
 
    def enqueue_new_children(s):
        # aslog(0) << "\n** Generated child: "
        # s->dump()
        # s->calculate_cost(dag, params, nullptr, true)

        # Each child should have one more decision made than its parent state.
        assert(s.num_decisions_made == s.parent.num_decisions_made + 1)

        progress = s.num_decisions_made * beam_size + expanded
        max_progress = dag.nodes.size() * beam_size * 2

        # Update the progress bar
        tick.set(progress / max_progress)
        s.penalized = False

        # Add the state to the list of states to evaluate
        q.emplace(s)
     

    cyos_str = os.getenv("HL_CYOS")

    # This loop is beam search over the sequence of decisions to make.
    while True:
        hashes = {}
        q.swap(pending)

        if pending.empty():
            if (False and beam_size < 1000):
                # Total mortality. Double the beam size and
                # restart. Disabled for now because total mortality
                # may indicate a bug.
                # 下面一行代码似乎有问题
                return optimal_schedule_pass(dag, vector(outputs), params, cost_model, rng, beam_size * 2, int64_t(memory_limit), pass_idx, num_passes, tick, permitted_hashes)
            else:
                print( "Ran out of legal states with beam size " , beam_size )

        if int(pending.size()) > beam_size * 10000:
            print("Warning: Huge number of states generated (" ,pending.size(), ").\n")






        expanded = 0
        while expanded < beam_size and not pending.empty():

            state = pending.pop()

            if beam_size > 1 and num_passes > 1:
                # We are doing coarse-to-fine beam search using the
                # hashing strategy mentioned in the paper.
                #
                # We will lazily apply cost penalties to the queue
                # according to structural uniqueness.
                if not state.penalized:
                    h1 = state.structural_hash(pass_idx + 1)
                    h0 = state.structural_hash(pass_idx - 1)
                    # We penalize the cost of a state proportionately
                    # to how many states we've already seen with that
                    # hash.

                    penalty += hashes[h1]
                    if pass_idx > 0 and not permitted_hashes.count(h0):
                        # It's possible to get yourself into a state
                        # where the only things in the beam that match
                        # the hash were quick-rejected due to details not
                        # captured in the hash, so we apply a huge
                        # penalty, but leave the impermissible state in
                        # the beam.
                        penalty += 10
                    if penalty > 1:
                        state.penalized = True
                        state.cost *= penalty
                        # After penalizing this state, if it's no
                        # longer the best, defer it. We set the
                        # 'penalized' flag so that we know not to
                        # penalize and defer it again.
                        if (not pending.empty()) and state.cost > pending.top().cost:
                            pending.emplace(state)
                            continue

            # Random dropout
            if pending.size() > 1 and random_dropout(rng, dag.nodes.size() * 2):
                continue

            if state.num_decisions_made == 2 * int(dag.nodes.size()):
                # We've reached the end of the pass. The first state
                # must be the best, because we're pulling off a
                # priority queue.
                best = state

                # Bless the reasonable stuff in the beam as
                # permissible states to visit again. We define
                # reasonable as having a cost no more than 20% higher
                # than the cost of the best thing. Only do this if
                # there are more coarse-to-fine passes yet to come.
                if pass_idx + 1 < num_passes:
                    blessed = 0
                    while state.cost <= 1.2 * best.cost and blessed < beam_size:
                        s = state.get()
                        while s != None:
                            h1 = s.structural_hash(pass_idx)
                            permitted_hashes.insert(h1)
                            s = s.parent.get()
                        if pending.empty():
                            break
                        state = pending.pop()
                        blessed += 1

                return best

            state.generate_children(dag, params, cost_model, memory_limit, enqueue_new_children)
            expanded += 1

        # Drop the other states unconsidered.
        pending.clear()


        if cost_model != None:
            # Now evaluate all the costs and re-sort them in the priority queue
            cost_model.evaluate_costs()
            q.resort()

        if cyos_str is "1":
            # The user has set HL_CYOS, and wants to navigate the
            # search space manually.  Discard everything in the queue
            # except for the user-chosen option.
            print( "\n--------------------\n")
            print( "Select a schedule:\n")
            for choice_label in range(int(q.size()) - 1, 0, -1):
                state = q[choice_label]
                print( "\n[" << choice_label << "]:\n")
                state.dump()
                state.calculate_cost(dag, params, cost_model, memory_limit, True)
            cost_model.evaluate_costs()

            # Select next partial schedule to expand.
            selection = -1
            while selection < 0 or selection >= int(q.size()):
                selection=input( "\nEnter selection: ")
                
            selected = q[selection]
            selected.dump()
            q.clear()
            q.emplace(selected)

################# line 175 state ########################
class State(object):

    def _initialize_instance_fields(self):
        self.ref_count = RefCount()
        self.root = IntrusivePtr()
        self.parent = IntrusivePtr()
        self.cost = 0
        self.num_decisions_made = 0
        self.penalized = False

# ???
#    State() = default
#    State(const State &) = delete
#    State(State &&) = delete
#    void operator =(const State &) = delete
#    void operator =(State &&) = delete

    cost_calculations = 0
    def structural_hash(self, depth):
        h = self.num_decisions_made
        assert(self.root.defined())
        self.root.structural_hash(h, depth)
        return h

    # Compute the parent and depth of every loop nest node
    def compute_loop_nest_parents(self, p, here, depth):
        for c in here.children:
            p.emplace(c.get(), pair<const LoopNest *, int>({here, depth})) #???
            self.compute_loop_nest_parents(p, c.get(), depth + 1)

    def deepest_common_ancestor(self, parent, a, b):
        if a.is_root():
            return a
        if b.is_root():
            return b
        if a is b:
            return a

        # Walk the deeper one up until they're at the same depth
        it_a = parent.find(a)
        it_b = parent.find(b)
        assert(it_a != parent.end() and it_b != parent.end())
        while it_a.second.second > it_b.second.second:
            a = it_a.second.first
            it_a = parent.find(a)
        while it_b.second.second > it_a.second.second:
            b = it_b.second.first
            it_b = parent.find(b)

        while True:
            # Walk each up one
            a = it_a.second.first
            b = it_b.second.first
            if a is b:
                return a
            it_a = parent.find(a)
            it_b = parent.find(b)
            assert(it_a != parent.end() and it_b != parent.end())

        # unreachable
        return None #???



def compute_featurization(self, dag, params, features):
    sites = StageMap()
    sites.make_large(dag.nodes[0].stages[0].max_id)
    features.make_large(dag.nodes[0].stages[0].max_id)
    assert(root.defined())
    root.get_sites(sites)

    # For the input nodes and unscheduled outputs, the compute
    # and store sites are root, and the produce and innermost
    # sites are unset (nullptr)
    for n in dag.nodes:
        if n.is_input or n.is_output:
            for stage in n.stages:
                s = sites.get_or_create(stage)
                if s.compute is None:
                    s.compute = root.get()
                    s.store = root.get()

    # For the unscheduled nodes, give them sites as deep as they
    # could possibly be. We'll ignore the possibility of inlining
    # them for now.
    parent = map()
    compute_loop_nest_parents(parent, root.get(), 0)
    for n in dag.nodes:
        if sites.contains((n.stages[0])):
            continue
        loop = None
        for e in n.outgoing_edges:
            consumer_site = sites.get(e.consumer)
            l = consumer_site.innermost
            if l == None:
                l = consumer_site.compute
            if l == None:
                if aslog.aslog_level() > 0:
                    dump()
                internal_error << e.producer.func.name() << " -> " << e.consumer.name << "\n"
            if loop != None:
                loop = deepest_common_ancestor(parent, l, loop)
            else:
                loop = l
        if not loop :
            print( "Could not compute plausible site for unscheduled Func: " , n.func.name() ,"\n")
        for stage in n.stages:
            site = sites.get_or_create(stage)
            site.compute = loop
            site.store = loop

    root.compute_features(dag, params, sites, 1, 1, None, None, *root, None, features)

    for n in dag.nodes:
        if sites.get((n.stages[0])).produce is None:
            if not features.contains((n.stages[0])):
                print( "Somehow an input or unscheduled node ended up in the featurization: " , n.func.name() , "\n")
############################### line 308  ##############################

##################### line 309 -


def save_featurization(self, dag, params, out):
    features = StageMap()
    compute_featurization(dag, params, features)

    for n in dag.nodes:
        if n.is_input:
            continue
        for stage_idx in range(n.stages.size(), 1, -1):
            s = n.stages[stage_idx - 1]
            num_schedule_features = ScheduleFeatures.num_features()
            num_pipeline_features = PipelineFeatures.num_features()
            sched_feat = features.get(s)

            buf = [0 for _ in range(num_schedule_features + num_pipeline_features)]
            # Save them as floats
            while i < num_schedule_features:
                buf[i] = sched_feat[i]
            i += 1

            while i < num_pipeline_features:
                buf[i + num_schedule_features] = s.features[i]
            i += 1


            out.write(buf, len(buf))


def calculate_cost(self, dag, params, cost_model, memory_limit, verbose = False):
    features = StageMap()
    compute_featurization(dag, params, features)

    cost = 0

    # if verbose:
    #     while it is not features.end():
    #         stage = *(it.key())
    #         feat = it.value()
    #         print( "Schedule features for " , stage.stage.name() , "\n")
    #         feat.dump()
    #     it += 1

    assert(cost_model)

    # Perform some addition pruning before burdening the cost model with silly states
    while it is not features.end():
        if not it.key().node.is_wrapper:
            feat = it.value()
            if feat.points_computed_total + feat.inlined_calls > 8 * feat.points_computed_minimum:
                cost = 1e50
                return False
    it += 1
    # Avoid code size explosion from recursive inlining.
    if root.max_inlined_calls() >= 256:
        cost = 1e50
        return False
    # Apply the hard limit on memory use
    if memory_limit >= 0:
        mem_used = features.begin().value().working_set_at_root
        while it is not features.end():
            if it.key().node.is_output or it.key().node.is_input:
                # Not allocated by this pipeline
                mem_used -= it.value().bytes_at_production
        it += 1
        if mem_used > memory_limit:
            cost = 1e50
            return False
    # Tell the cost model about this state. It won't actually
    # evaluate it until we call evaluate_costs (or if it runs out
    # of internal buffer space), so that the evaluations can be
    # batched.
    cost_model.enqueue(dag, features, cost)

    cost_calculations += 1
    return True
# Make a child copy of this state. The loop nest is const (we
# make mutated copies of it, rather than mutating it), so we can
# continue to point to the same one and so this is a cheap
# operation.
def make_child(self):
    s = State()
    s.parent = self
    s.root = root
    s.cost = cost
    s.num_decisions_made = num_decisions_made
    return s

# Generate the successor states to this state
def generate_children(self, dag, params, cost_model, memory_limit, accept_child):
    assert(root.defined() and root.is_root())

    if num_decisions_made == 2 * int(dag.nodes.size()):
        return
    next_node = num_decisions_made / 2
    phase = num_decisions_made % 2

    if not may_subtile():
        # When emulating the older search space, we do all
        # parallelizing last, so that it is independent of the
        # tiling decisions.
        next_node = num_decisions_made % dag.nodes.size()
        phase = num_decisions_made / dag.nodes.size()

    # Enumerate all legal ways to schedule the next Func
    node = dag.nodes[next_node]
    for e in node.outgoing_edges:
        if not (root.computes(e.consumer.node)): 
            print( "Partially scheduled code doesn't compute " , e.consumer.name , ", which is one of the consumers of " , node.func.name())

    if node.is_input:
        # We don't need to schedule nodes that represent inputs,
        # and there are no other decisions to be made about them
        # at this time.
        # aslog(0) << "Skipping over scheduling input node: " << node->func.name() << "\n"
        child = make_child()
        child.num_decisions_made += 1
        accept_child(std::move(child))
        return

    if (not node.outgoing_edges.empty()) and not root.calls(node):
        print( "In state:\n")
        dump()
        print( node.func.name() , "is consumed by\n")
        for e in node.outgoing_edges:
            print( e.consumer.name )
            print( "Which in turn consumes:\n")
            for e2 in e.consumer.incoming_edges:
                print("  " , e2.producer.func.name() , "\n")
        print( "internal_error, Pipeline so far doesn't use next Func: ", node.func.name() , "\n")

####################### line 464 #######################
    num_children = 0

    if (phase == 0):
        # Injecting realizations
            # 1) Inline it
            if node.stages.size() == 1 and not node.is_output:
                child = make_child()
                new_root = LoopNest()
                new_root.copy_from(*root)
                new_root.inline_func(node)
                child.root = new_root
                child.num_decisions_made += 1
                if child.calculate_cost(dag, params, cost_model, memory_limit):
                    num_children += 1
                    accept_child(std::move(child))#???

        # Some search-space pruning. If a node is pointwise, and
        # so are all its inputs and so is its sole output, and
        # inlining it is legal, just inline it. This saves time
        # on long chains of pointwise things.
        must_inline = (node.is_pointwise and (num_children > 0) and (node.outgoing_edges.size() == 1))

        if must_inline:
            for e in node.stages[0].incoming_edges:
                must_inline &= e.producer.is_pointwise
            for e in node.outgoing_edges:
                must_inline &= (e.consumer.node.is_pointwise or e.consumer.node.is_boundary_condition)
            if must_inline:
                return

        # Construct a list of plausible dimensions to vectorize
        # over. Currently all of them. 
        vector_dims = vector()
        if (not node.is_input) and not node.is_output:
            while v < node.dimensions:
                p = root.get_bounds(node).region_computed(v)
                if p.extent() >= node.vector_size:
                    vector_dims.push_back(v)
            v += 1

        # Outputs must be vectorized over their innermost
        # dimension, because we don't have control of the
        # storage. Infer which dimension(s) is(are) the innermost one(s) by
        # looking at the stride. Note that there can be more than one in
        # case some dimensions have an extent of 1.
        i=0
        if node.is_output and not node.func.output_buffers().empty():
            output = node.func.output_buffers()[0]
            num_dims = output.dimensions()
            while i < num_dims:
                stride = output.stride_constraint(i)
                s = as_const_int(stride)
                if s != None and s == 1:
                    vector_dims.push_back(i)
            i += 1
        v=0
        if vector_dims.empty():
            # This can happen if the output strides aren't known, or if all
            # the dimensions are smaller than the vector size.
            # TBD: consider extending compute_in_tiles to support -1 as a
            # vector dim to indicate no vectorization.
            while v < node.dimensions:
                vector_dims.push_back(v)
            v += 1
            # Handle the case of full reductions that generate a scalar.
            # We need at least one vector dimension to call cmopute_in_tiles
            # below.
            # TBD: figure out a better fallback strategy.
            if vector_dims.empty():
                vector_dims.push_back(0)

############################ line 554 ##########################################
        # 2) Realize it somewhere
        for vector_dim in vector_dims:
            tile_options = root.compute_in_tiles(node, None, params, vector_dim, False)
            for n in tile_options:
                child = make_child()
                child.root = std::move(n)
                child.num_decisions_made += 1
                if child.calculate_cost(dag, params, cost_model, memory_limit):
                    num_children += 1
                    accept_child(std::move(child))
        else:
            should_parallelize = False
            pure_size = None
            if params.parallelism > 1:
                for c in root.children:
                    if c.node == node and node.dimensions > 0:
                        if c.stage.index == 0:
                            pure_size = c.size
                        should_parallelize = True
            if not should_parallelize:
                num_children += 1
                child = make_child()
                child.num_decisions_made += 1
                accept_child(std::move(child))

            else:
                assert(pure_size)
                tilings = generate_tilings(*pure_size, node.dimensions - 1, 2, True)
                ones = []
                ones.resize(len(pure_size), 1)
                tilings.emplace_back(std::move(ones))
                struct Option
                    tiling = vector()
                    idle_core_wastage = None
                    entire = None
                    bool operator <(Option &other) 
                        return idle_core_wastage , other.idle_core_wastage
                        
                    Option() = default
                    Option(Option) = default
                    operator = (Option) = default
                    Option(Option) = delete
                    operator = (Option) = delete
                options = vector()
                i = 0
                while i < tilings.size():
                    t = tilings[i]
                    o = Option()
                    o.entire = (i is tilings.size() - 1)

                    j = 0
                    while j < pure_size.size():
                        t[j] = ((*pure_size)[j] + t[j] - 1) / t[j]
                        j += 1
                    t.swap(o.tiling)
                    min_total = 0
                    max_total = 0
                    o.idle_core_wastage = 1
                    for c in root.children:
                        if c.node == node:
                            total = 1
                            for l in c.stage.loop:
                                if not l.rvar:
                                    total *= o.tiling[l.pure_dim]
                            if min_total != 0:
                                min_total = min(min_total, total)
                            else:
                                min_total.copy_from(total)
                            max_total = max(max_total, total)
                            tasks_per_core = (float(total)) / params.parallelism
                            o.idle_core_wastage = max(o.idle_core_wastage, math.ceil(tasks_per_core) / tasks_per_core)
                    ok = ((o.entire or min_total >= params.parallelism) and (max_total <= params.parallelism * 16))

                    if not ok:
                        continue
                    options.emplace_back(std::move(o))
                    i += 1
                std::sort(options.begin(), options.end()) #comm
                if options.empty():
                    num_children += 1
                    child = make_child()
                    child.num_decisions_made += 1
                    accept_child(std::move(child))
                    return
                for o in options:
                    if num_children >= 1 and (o.idle_core_wastage > 1.2 or (not may_subtile())):
                        break
                    child = make_child()
                    new_root = LoopNest()
                    new_root.copy_from(*root)
                    for c in new_root.children:
                        if c.node == node:
                            if may_subtile():
                                c = c.parallelize_in_tiles(params, o.tiling, new_root)
                            else:
                                tiling = c.size
                                total = 1
                                for i in range(c.size.size(), 1, -1):
                                    if (not c.stage.loop[i - 1].pure) or total >= params.parallelism:
                                        tiling[i - 1] = 1
                                    while tiling[i - 1] > 1 and total * tiling[i - 1] > params.parallelism * 8 != None:
                                        tiling[i - 1] /= 2
                                    total *= tiling[i - 1]
                                c = c.parallelize_in_tiles(params, tiling, new_root)
                    child.root = new_root
                    child.num_decisions_made += 1
                    if child.calculate_cost(dag, params, cost_model, memory_limit):
                        num_children += 1
                        accept_child(std::move(child))

        if num_children == 0:
            print( "Warning: Found no legal way to schedule " ,node.func.name() , " in the following State:\n")
            dump()
######################### line 729 ####################################


#############  line 730 -line 883  ############# 

def dump(self):
    print( "State with cost " , cost)
    root.dump("", None)
    print(schedule_source)

schedule_source = ''

# Apply the schedule represented by this state to a Halide
# Pipeline. Also generate source code for the schedule for the
# user to copy-paste to freeze this schedule as permanent artifact.

def apply_schedule(self, dag, params):
    state_map = StageMap()
    root.apply(root(), state_map, params.parallelism, 0, None, None)

    # Print handles for all the Funcs
    i = int((dag.nodes.size() - 1))
    for n in dag.nodes:
        if not n.is_input:
            print( "Func " , n.func.name() , " = pipeline.get_func(" , i )
        i -= 1

    # Gather all Vars and RVars so that we can declare them in the emitted source
    vars = map()
    rvars = map()
    for p in state_map:
        for v in p.second.vars:
            if v.exists:
                if v.var.is_rvar:
                    rvars.emplace(v.var.name(), v.accessor)
                else:
                    vars.emplace(v.var.name(), v.accessor)
    if not vars.empty():
        for p in vars:
            if p.second.empty():
                print( "Var " , p.first , "(\"" , p.first , "\)")
            else:
                print( "Var " , p.first , "(" , p.second , ")")
    if not rvars.empty():
        for p in rvars:
            if p.second.empty():
                print( "RVar " , p.first , "(\"" , p.first , "\")")
            else:
                print( "RVar " , p.first , "(" , p.second , ")")

    for p in state_map:
        if p.first.node.is_input:
            continue

        stage = Stage(p.first.stage)

        # Do all the reorders and pick which vars to
        # parallelize.
        vars = vector()
        parallel_tasks = 1
        parallel_vars = vector()
        any_parallel_vars = False
        any_parallel_rvars = False
        while it is not p.second.vars.rend():
            if (not it.exists) or it.extent == 1:
                continue
            if not it.parallel:
                break
            any_parallel_rvars |= it.var.is_rvar
            any_parallel_vars |= not it.var.is_rvar
            parallel_tasks *= it.extent
            parallel_vars.push_back(it.var)
        it += 1

        if p.second.vars.size() > 1:
            p.second.schedule_source << "\n    .reorder("
            first = True
            for v in p.second.vars:
                if v.exists:
                    vars.push_back(v.var)
                    if not first:
                        p.second.schedule_source << ", "
                    else:
                        p.second.schedule_source << "{"
                    first = False
                    p.second.schedule_source << v.var.name()
            p.second.schedule_source << "})"
            stage.reorder(vars)



        # Halide doesn't let you fuse an RVar with a Var, even if
        # they are both pure.
        can_fuse = not(any_parallel_vars and any_parallel_rvars)
        if (can_fuse):
            while i < parallel_vars.size():
                # Outermost, and next outermost. Preserve the inner
                # name to not invalidate any compute_ats.
                p.second.schedule_source << "\n    .fuse(" << parallel_vars[i].name() << ", " << parallel_vars[i - 1].name() << ", " << parallel_vars[i].name() << ")"
                stage.fuse(parallel_vars[i], parallel_vars[i - 1], parallel_vars[i])
            i += 1
            if not parallel_vars.empty():
                p.second.schedule_source << "\n    .parallel(" << parallel_vars.back().name() << ")"
                stage.parallel(parallel_vars.back())
        else:
            for v in parallel_vars:
                p.second.schedule_source << "\n    .parallel(" << v.name() << ")"
                stage.parallel(v)

        # Reorder the vector dimension innermost
        if p.first.index == 0 and p.second.vector_dim > 0:
            storage_vars = Func(p.first.node.func).args()
            for i in range(p.second.vector_dim, 1, -1):
                std::swap(storage_vars[i], storage_vars[i - 1])
            p.second.schedule_source << "\n    .reorder_storage("
            first = True
            for v in storage_vars:
                if not first:
                    p.second.schedule_source << ", "
                first = False
                p.second.schedule_source << v.name()
            p.second.schedule_source << ")"
            Func(p.first.node.func).reorder_storage(storage_vars)

        # Dump the schedule source string
        src << p.first.name << p.second.schedule_source.str() << ";\n"
        # Sanitize the names of things to make them legal source code.
        schedule_source = src.str()
        in_quotes = False
        for c in schedule_source:
            in_quotes ^= (c == '"')
            if (not in_quotes) and c == '$':
                c = '_'


############# line 883  ############# 






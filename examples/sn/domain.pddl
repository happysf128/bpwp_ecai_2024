;Header and description
(define 
    (domain sn)

    ;define actions here
    (:action a_friends
        :parameters (?a - agent)
        :precondition (and 
        ; to do
            (= (:ontic (= (friended a ?a) 0)) 1)
        )
        :effect (and 
            (= (friended a ?a) 1)
            (= (friended ?a a) 1)
        )
    )

    (:action a_unfriends
        :parameters (?a - agent)
        :precondition (and 
        ; to do
            (= (:ontic (= (friended a ?a) 1)) 1)
        )
        :effect (and 
            (= (friended a ?a) 0)
            (= (friended ?a a) 0)
        )
    )

    (:action a_post
        :parameters (?a - agent, ?p - object)
        :precondition (and 
        ; to do
            (= (:ontic (= (friended a ?a) 1)) 1)
            (= (:ontic (= (post ?p ?a) 0)) 1)
        )
        :effect (and 
            (= (post ?p ?a) 1)
        )
    )

    (:action a_unpost
        :parameters (?a - agent, ?p - object)
        :precondition (and 
        ; to do
            (= (:ontic (= (friended a ?a) 1)) 1)
            (= (:ontic (= (post ?p ?a) 1)) 1)
        )
        :effect (and 
            (= (post ?p ?a) 0)
        )
    )

)
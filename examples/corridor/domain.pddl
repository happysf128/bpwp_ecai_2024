;Header and description
(define 
    (domain corridor)

    ;remove requirements that are not needed
    ; (:requirements :strips)

    ; (:types ;todo: enumerate types and their hierarchy here, e.g. car truck bus - vehicle
    ; )

    ; un-comment following line if constants are needed
    ;(:constants )

    ; (:predicates ;todo: define predicates here
    ; )


    ; (:functions ;todo: define numeric functions here
    ; )

    ;define actions here
    (:action move_a_right
        :parameters ()
        :precondition (and )
        :effect (and 
            (= (agent_at-a) (+1))
        )
    )
    
    (:action move_a_left
        :parameters ()
        :precondition (and )
        :effect (and 
            (= (agent_at-a) (-1))
        )
    )

    (:action sense
        :parameters (?s - object)
        :precondition (and 
            (= (:ontic (= (agent_at-a) (secret_at ?s))) 1)
        )
        :effect (and 
            (= (sensed ?s) 't') 
        )
    )

    (:action shout
        :parameters (?s - object)
        :precondition (and 
            (= (:ontic (= (sensed ?s) 't')) 1)
        )
        :effect (and 
            (= (shared ?s) (agent_at-a))
            (= (secret ?s) 't')
        )
    )

    (:action shout_lie
        :parameters (?s - object)
        :precondition (and 
            (= (:ontic (= (sensed ?s) 't')) 1)
        )
        :effect (and 
            (= (shared ?s) (agent_at-a))
            (= (secret ?s) 'f')
        )
    )

)
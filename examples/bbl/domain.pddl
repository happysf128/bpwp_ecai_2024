;Header and description

(define 
    (domain bbl)

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
    (:action turn_clockwise
        :parameters (?i - agent)
        :precondition (and )
        :effect (and 
            (= (dir ?i) ( + 1))
        )
    )
    
    (:action turn_counter_clockwise
        :parameters (?i - agent)
        :precondition (and )
        :effect (and 
            (= (dir ?i) ( - 1))
        )
    )
 
)
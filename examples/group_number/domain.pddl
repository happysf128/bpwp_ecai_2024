;Header and description

(define 
    (domain group_number)

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
    ; (:action peek
    ;     :parameters (?i - agent)
    ;     :precondition (and 
    ;         ;(= (peeking ?i) 'f')
    ;         (= (:ontic (= (peeking ?i) 'f')) 1)
    ;     )
    ;     :effect (and 
    ;         (= (peeking ?i) 't')
            
    ;     )
    ; )

    (:action single_peek
        :parameters (?i - agent)
        :precondition (and 
            (= (:ontic (= (peeking-a) 'f')) 1)
            (= (:ontic (= (peeking-b) 'f')) 1)
        )
        :effect (and 
            (= (peeking ?i) 't')
            
        )
    )

    (:action return
        :parameters (?i - agent)
        :precondition (and 
            ; (= (peeking ?i) 't')
            (= (:ontic (= (peeking ?i) 't')) 1)
        )
        :effect (and 
            (= (peeking ?i) 'f')
        )
    )

    (:action addition1
        :parameters (?i - object)
        :precondition (and )
        :effect (and 
            (= (num ?i) (+1)))
        )
    )

    (:action subtraction1
        :parameters (?i - object)
        :precondition (and )
        :effect (and 
            (= (num ?i) (-1)))
        )
    )
)
; depth 3 agent 7
(define 
    (problem corridor104) 
    (:domain corridor)

    (:agents
        a b c d e f g
    )
    (:objects 
        s
    )

    (:variables
        (agent_at [a,b,c])
        (secret_at [s])
        (sensed [s])
        (shared [s])
        (secret [s])
    )

    (:init
        (= (agent_at a) 1)
        (= (agent_at b) 2)
        (= (agent_at c) 3)
        (= (secret_at s) 2)
        ; the valid room is 1-4 only, zero means not done it yet
        
        (= (shared s) 0)

        (= (sensed s) 'f')
        (= (secret s) 't')
        ;todo: put the initial state's facts and numeric values here
    )

    (:goal (and
        ; (= (:ontic (= (agent_at a) 2)) 1)
        ; (= (:ontic (= (shared s) 2)) 1)
        (= (:epistemic b [b] k [b] k [b] (= (secret s) 't')) 0)
        (= (:epistemic b [c] (= (secret s) 't')) 1)
        ; (= (:epistemic k [b] k [a] (= (v p) 't')) 0)
        ; (= (:epistemic s [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic k [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic s [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [b] (= (v p) 't')) 1)
        ;todo: put the goal condition here
    ))

    (:domains
        (agent_at integer [1,4])
        (secret_at integer [1,4])
        (shared integer [0,4])
        (sensed enumerate ['t','f'])
        (secret enumerate ['t','f'])
        ; the following line is the default
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)
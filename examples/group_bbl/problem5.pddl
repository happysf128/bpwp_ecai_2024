(define 
    (problem group_bbl05) 
    (:domain group_bbl)

    (:agents
        a b
    )
    (:objects 
        o p q
    )

    (:variables
        (dir [ a , b ])
        (x [a,b,o,p,q])
        (y [a,b,o,p,q])
        (v [o,p,q])
    )

    (:init
        (= (dir a) 'sw')
        (= (x a) 3)
        (= (y a) 3)

        (= (dir b) 'n')
        (= (x b) 1)
        (= (y b) 1)

        (= (x o) 0)
        (= (y o) 0)
        (= (v o) 1)

        (= (x p) 2)
        (= (y p) 2)
        (= (v p) 2)

        (= (x q) 4)
        (= (y q) 4)
        (= (v q) 3)


        ;todo: put the initial state's facts and numeric values here
    )

    (:goal (and
        ; (= (:ontic (= (dir b) 'se')) 1)
        ; (= (:epistemic cb [a,b] (< (v o) (v q))) 1)
        (= (:epistemic eb [a,b] (= (v o) 1)) 1)
        (= (:epistemic eb [a,b] (= (v p) 2)) 1)
        (= (:epistemic eb [a,b] (= (v q) 3)) 1)
        ; (= (:epistemic cb [a,b] (= (v p) 2)) 0)
        ; (= (:epistemic k [b] k [a] (= (v p) 't')) 0)
        ; (= (:epistemic s [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic k [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic s [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [b] (= (v p) 't')) 1)
        ;todo: put the goal condition here
    ))

    (:domains
        (dir enumerate ['w','nw','n','ne','e','se','s','sw'])
        (x integer [0,4])
        (y integer [0,4])
        (v integer [0,4])
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)
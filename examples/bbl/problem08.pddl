

( define 
    (problem bbl08) 
    (:domain bbl)

    (:agents
        a b
    )
    (:objects 
        p
    )

    (:variables
        (dir [ a , b ])
        (x [a,b,p])
        (y [a,b,p])
        (v [p])
    )

    (:init
        (= (dir a) 'sw')
        (= (dir b) 'n')
        (= (x a) 3)
        (= (x b) 2)
        (= (x p) 1)
        (= (y a) 3)
        (= (y b) 2)
        (= (y p) 1)
        (= (v p) 't')
        ;todo: put the initial state's facts and numeric values here
    )

    (:goal (and
        ; (= (:ontic (= (dir b) 'se')) 1)
        ; (= (:epistemic b [b] (= (v p) 't')) 1)
        ; (= (:epistemic k [b] k [a] (= (v p) 't')) 0)
        (= (:epistemic b [a] b [b] b [a] b [b] (= (v p) 't')) 1)
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
        (v enumerate ['t','f'])
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)


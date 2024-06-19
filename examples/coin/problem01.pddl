( define 
    (problem coin01) 
    (:domain coin)

    (:agents
        a b
    )
    (:objects 
        c
    )

    (:variables
        (peeking [ a , b ])
        (face [c])
    )

    (:init
        (= (peeking a) 'f')
        (= (peeking b) 'f')
        (= (face c) 'head')
        ;todo: put the initial state's facts and numeric values here
    )

    (:goal (and
        ; (= (:ontic (= (dir b) 'se'))
        (= (:epistemic b [a] (= (face c) 'head')) 1)
        ; (= (:epistemic b [b] (= (face c) 'tail')) 1)
        ; (= (:epistemic b [b] b [a] (= (face c) 'head')) 1)
        ; (= (:epistemic b [b] (= (face c) 'head')) 1)
        ; (= (:epistemic k [b] k [a] (= (v p) 't')) 0)
        ; (= (:epistemic s [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic k [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic s [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [b] (= (v p) 't')) 1)
        ;todo: put the goal condition here
    ))

    (:domains
        ; (dir enumerate ['w','nw','n','ne','e','se','s','sw'])
        ; (x integer [0,4])
        ; (y integer [0,4])
        (peeking enumerate ['t','f'])
        (face enumerate ['head','tail'])
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)

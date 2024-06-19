
(define 
    (problem grapevine807) 
    (:domain grapevine8)

    (:agents
        a b c d e f g h
    )
        
    (:objects
        p
    )

    (:variables
        (agent_at [a,b,c,d,e,f,g,h])
        (shared [a,b,c,d,e,f,g,h])
        (secret [a,b,c,d,e,f,g,h])
    )

    (:init
        (= (agent_at a) 1)
        (= (agent_at b) 1)
        (= (agent_at c) 1)
        (= (agent_at d) 1)


        (= (shared a) 0)
        (= (shared b) 0)
        (= (shared c) 0)
        (= (shared d) 0)      

        ; constant dummy value to represent knows one's secret_at
        (= (secret a) 't')
        (= (secret b) 't')  
        (= (secret c) 't')  
        (= (secret d) 't')    

        (= (agent_at e) 1)
        (= (agent_at f) 1)
        (= (agent_at g) 1)
        (= (agent_at h) 1)
        (= (shared e) 0)
        (= (shared f) 0)
        (= (shared g) 0)
        (= (shared h) 0)
        (= (secret e) 't')
        (= (secret f) 't')  
        (= (secret g) 't')  
        (= (secret h) 't')       
    )

    (:goal (and
        ; (= (:ontic (= (agent_at a) 2)) 1)
        ; (= (:ontic (= (shared a) 2)) 1)
        (= (:epistemic b [b] (= (secret a) 't')) 1)
        (= (:epistemic b [c] (= (secret a) 'f')) 1)
        ; (= (:epistemic b [d] (= (secret a) 't')) 0)
        ; (= (:epistemic k [b] k [a] (= (v p) 't')) 0)
        ; (= (:epistemic s [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic k [b] s [a] (= (v p) 't')) 2)
        ; (= (:epistemic s [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [a] (= (v p) 't')) 1)
        ; (= (:epistemic b [b] (= (v p) 't')) 1)
        ;todo: put the goal condition here
    ))

    (:domains
        (agent_at integer [1,2])
        (shared integer [0,2])
        (secret enumerate ['t','f'])
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)
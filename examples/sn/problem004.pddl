
(define 
    (problem sn04) 
    (:domain sn)

    (:agents
        a b c d e
    )
        
    (:objects
        p1 p2
    )

    (:variables
        (friended [a,b,c,d,e] [a,b,c,d,e])
        ; (b_follows [a,b,c,d,e])
        ; (c_follows [a,b,c,d,e])
        ; (d_follows [a,b,c,d,e])
        ; (e_follows [a,b,c,d,e])
        ; (p1_posted [a,b,c,d,e])
        ; (p2_posted [a,b,c,d,e])
        (post [p1,p2] [a,b,c,d,e])
        (secret [p1,p2])
    )

    (:init
        (= (friended c a) 1)
        (= (friended c b) 1)
        (= (friended c c) 1)
        (= (friended c d) 1)
        (= (friended c e) 0)
        
        (= (friended b a) 0)
        (= (friended b b) 1)
        (= (friended b c) 1)
        (= (friended b d) 0)
        (= (friended b e) 1)
        
        (= (friended a a) 1)
        (= (friended a b) 0)
        (= (friended a c) 1)
        (= (friended a d) 1)
        (= (friended a e) 0)
        
        (= (friended d a) 1)
        (= (friended d b) 0)
        (= (friended d c) 1)
        (= (friended d d) 1)
        (= (friended d e) 1)
        
        (= (friended e a) 0)
        (= (friended e b) 1)
        (= (friended e c) 0)
        (= (friended e d) 1)
        (= (friended e e) 1)

        (= (post p1 a) 0)
        (= (post p1 b) 0)
        (= (post p1 c) 0)
        (= (post p1 d) 0)
        (= (post p1 e) 0)

        (= (post p2 a) 0)
        (= (post p2 b) 0)
        (= (post p2 c) 0)
        (= (post p2 d) 0)
        (= (post p2 e) 0)

        (= (secret p1) 't')
        (= (secret p2) 't')
        ; (= ((a_follows a)) 1)
        ; (= ((a_follows b)) 1)
        ; (= ((a_follows c)) 1)
        ; (= ((a_follows d)) 1)
        ; (= ((a_follows e)) 0)
      
    )

    (:goal (and
        ; (= (:ontic (= (agent_at a) 2)) 1)
        ; (= (:ontic (= (post p1 a) 1)) 1)
        (= (:epistemic b [a] (= (secret p1) 't')) 1)
        (= (:epistemic b [b] (= (secret p1) 't')) 1)
        (= (:epistemic b [c] (= (secret p1) 't')) 1)
        (= (:epistemic b [d] (= (secret p1) 't')) 1)
        (= (:epistemic b [e] (= (secret p1) 't')) 1)
        ; (= (:epistemic b [c] (= (secret a) 'f')) 1)
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
        (friended integer [0,1])
        (post integer [0,1])
        (secret enumerate ['t','f'])
        ;(epistemic epistemic ['1','0','2']) true false unknown
    )



    ;un-comment the following line if metric is needed
    ;(:metric minimize (???))
)
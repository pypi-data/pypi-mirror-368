(import toolz [first second])
(import hy-nrepl.ops.utils [ops])
(require hy-nrepl.ops.utils [defop])

(defop close [session msg transport]
  {"doc" "Closes the specified session"
   "requires" {"session" "The session to close"}
   "optional" {}
   "returns" {}}
  (.write session
          {"status" ["done"]
           "id" (.get msg "id")
           "session" session.id}
          transport)
  ;; registry is stored on the current session
  (try
    (let [sid (.get msg "session" "")] 
      (session.registry.remove sid))
    (except [e KeyError])))

;; Inspired by
;; https://github.com/clojure-emacs/cider-nrepl/blob/master/src/cider/nrepl/middleware/complete.clj

(import sys re inspect logging)

(import
  hy.macros
  hy.compiler
  hy.completer [Completer])

(import toolz [first second])
(import hy.reader.mangling [mangle unmangle])
(import hy-nrepl.ops.utils [ops])
(require hy-nrepl.ops.utils [defop])
(require hyrule [->])

(defn snake-to-kebab [s]
  (cond (= (len s) 0)
        ""

        (= (get s 0) "_")
        s

        :else
        (unmangle s)))

(defn kebab-to-snake [s]
  (if (= (len s) 0)
      ""
      (mangle s)))

(defn object-type [obj]
  (cond (inspect.isfunction obj) "function"
        (inspect.ismodule obj) "module"
        (inspect.isclass obj) "class"
        (inspect.ismethod obj) "method"
        (inspect.isbuiltin obj) "builtin"
        :else "other"))

(defn split-by-last-dot [text]
  (let [matches (re.match r"(\S+(\.[\w-]+)*)\.([\w-]*)$" text)]
    (if matches
        (.group matches 1 3)
        [text ""])))

(defclass TypedCompleter [hy.completer.Completer]
  (defn attr-matches [self text]
    (try
      (let [[expr attr-prefix] (split-by-last-dot text)
            obj (eval (kebab-to-snake expr) (. self namespace))
            words (dir obj)
            n (len attr-prefix)
            matches []]
        (for [w words]
          (when (= (cut w 0 n) (kebab-to-snake attr-prefix))
            (try
              (setv attr (getattr obj w))
              (setv attr-type (object-type attr))
              (.append matches
                       {"candidate" (.format "{}.{}" expr
                                             (if (= attr-type "module")
                                                 w
                                                 (snake-to-kebab w)))
                        "type" attr-type})
              (except [e Exception]
                (logging.error "Attribute error. text=`%s`, error=%s" text e)))))
        matches)
      (except [e NameError] [])
      (except [e Exception]
        (logging.error "Error in completions. text=`%s`, error=%s" text e)
        [])))

  (defn global-matches [self text]
    (let [matches []]
      (for [p (. self path)
            #(k v) (.items p)]
        (when (isinstance k str)
          (setv k (snake-to-kebab k))
          (when (.startswith k text)
            (.append matches {"candidate" k
                              "type" (object-type k)}))))
      matches)))

;; Sort completion candidates alphabetically
(defn sort-matches [matches]
  (sorted matches
          :key (fn [d]
                 (.get d "candidate"))))

;; Filter out private names unless the prefix starts with "_"
(defn filter-private-matches [matches prefix]
  (if (.startswith prefix "_")
      matches
      (lfor m matches
            :if (not (.startswith
                       (get (.split (.get m "candidate") ".")
                            (- (len (.split (.get m "candidate") ".")) 1))
                       "_"))
            m)))

(defn get-completions [session stem [extra None]]
  (let [comp (TypedCompleter (. session.module __dict__))]
    (cond
      (in "." stem)
      (-> (.attr-matches comp stem)
          (filter-private-matches (second (split-by-last-dot stem)))
          (sort-matches))

      True
      (-> (.global-matches comp stem)
          (filter-private-matches stem)
          (sort-matches)))))

;; completions
(defop "completions" [session msg transport]
  {"doc" "Returns a list of symbols matching the specified (partial) symbol."
   "requires" {"prefix" "The symbol to look up"}
   "optional" {"complete-fn" "The fully qualified name of a completion function to use instead of the default one (e.g. my.ns/completion)."
               "ns" "The namespace in which we want to obtain completion candidates. Defaults to *ns*."
               "options" "A map of options supported by the completion function. Supported keys: extra-metadata (possible values: :arglists, :docs)"}
   "returns" {"completions" "A list of possible completions"}}
  ;; (print "Complete: " msg :file sys.stderr)
  (.write session {"id" (.get msg "id")
                   "completions" (get-completions session (.get msg "prefix"))
                   "status" ["done"]}
          transport))
